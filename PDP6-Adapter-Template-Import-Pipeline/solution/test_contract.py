from dataclasses import FrozenInstanceError
import unittest
from main import (AdapterError, CsvLeadImporter, IntegrationError, Lead,
    LeadImportTemplate, WebhookLeadImporter, adapt_csv_row, adapt_webhook,
    fetch_leads, flag_high_score, run_pipeline)


class AdapterContracts(unittest.TestCase):
    def test_csv_versions_minimal_defaults_and_unknown_fields(self):
        self.assertEqual(adapt_csv_row({"email_address":" ADA@example.com ","score":" 7 ","extra":None}),Lead("ada@example.com","csv",7))
        self.assertEqual(adapt_csv_row({"version":"2","contact_email":"ADA@example.com","lead_score":"10"}),Lead("ada@example.com","csv",10))
        self.assertEqual(adapt_csv_row({"email_address":"a@b"}).score,0)

    def test_webhook_versions_and_nested_default_policy(self):
        self.assertEqual(adapt_webhook({"userEmail":" A@B ","priority":8}),Lead("a@b","webhook",8))
        self.assertEqual(adapt_webhook({"version":2,"contact":{"email":"A@B"},"ranking":{"score":9}}).score,9)
        self.assertEqual(adapt_webhook({"version":2,"contact":{"email":"A@B"}}).score,0)
        self.assertEqual(adapt_webhook({"userEmail":"a@b"}).score,0)

    def test_malformed_and_unknown_version_records_keep_validation_causes(self):
        for adapt,values in [(adapt_csv_row,[{}, {"version":3}, {"version":True}, {"email_address":None}, {"email_address":"a@b","score":"7.5"}]),(adapt_webhook,[{}, {"version":2,"contact":[]}, {"version":2,"contact":{"email":"a@b"},"ranking":None}, {"version":"1","userEmail":"a@b"}])]:
            for value in values:
                with self.subTest(value=value), self.assertRaises(AdapterError) as caught: adapt(value)
                self.assertIsInstance(caught.exception.__cause__,(KeyError,TypeError,ValueError))

    def test_scores_emails_and_internal_records_are_validated(self):
        for value in [True,1.5,"3",None,-1,11]:
            with self.assertRaises(AdapterError): adapt_webhook({"userEmail":"a@b","priority":value})
        for email in ["", "missing", "a@@b", "@b", "a@", "a @b"]:
            with self.assertRaises(AdapterError): adapt_csv_row({"email_address":email})
        with self.assertRaises(TypeError): Lead("a@b","csv",True)

    def test_models_and_inputs_do_not_share_mutable_vendor_state(self):
        raw={"version":2,"contact":{"email":"A@B"},"ranking":{"score":4}}
        value=adapt_webhook(raw); raw["contact"]["email"]="changed@x"
        self.assertEqual(value,Lead("a@b","webhook",4))
        with self.assertRaises(FrozenInstanceError): value.score=9

    def test_pipeline_and_template_preserve_order_and_equal_behavior(self):
        raw=[{"email_address":"B@X","score":"9"},{"email_address":"A@X","score":"7"}]
        expected=[Lead("b@x","csv",10),Lead("a@x","csv",7)]
        self.assertEqual(CsvLeadImporter().run(iter(raw)),expected)
        self.assertEqual(run_pipeline(iter(raw),adapt_csv_row,flag_high_score),expected)
        self.assertEqual(WebhookLeadImporter().run([{"userEmail":"a@x","priority":8}]),[Lead("a@x","webhook",10)])
        self.assertEqual(run_pipeline([],adapt_csv_row,flag_high_score),[])

    def test_pipeline_stops_at_first_failure_and_preserves_callback_identity(self):
        error=LookupError("transform"); calls=[]
        def transform(lead): calls.append(lead.email); raise error
        rows=[{"email_address":"a@x"},{"email_address":"b@x"}]
        with self.assertRaises(LookupError) as caught: run_pipeline(rows,adapt_csv_row,transform)
        self.assertIs(caught.exception,error); self.assertEqual(calls,["a@x"])

    def test_pipeline_validates_callable_and_return_contracts(self):
        with self.assertRaises(TypeError): run_pipeline([],None,flag_high_score)
        with self.assertRaises(TypeError): run_pipeline([{}],lambda row:{},flag_high_score)
        with self.assertRaises(TypeError): run_pipeline([{"email_address":"a@b"}],adapt_csv_row,lambda lead:None)
        with self.assertRaises(NotImplementedError): LeadImportTemplate().adapt({})

    def test_fetch_boundary_maps_call_and_iteration_io_failures_only(self):
        error=TimeoutError("vendor")
        def failed(): raise error
        def interrupted():
            yield {"email_address":"a@b"}
            raise error
        for fetch in [failed,interrupted]:
            with self.assertRaises(IntegrationError) as caught: fetch_leads(fetch,adapt_csv_row)
            self.assertIs(caught.exception.__cause__,error)
        bug=LookupError("programming")
        def broken(): raise bug
        with self.assertRaises(LookupError) as caught: fetch_leads(broken,adapt_csv_row)
        self.assertIs(caught.exception,bug)

    def test_threshold_and_injected_pipeline_comparison(self):
        for score,expected in [(0,0),(7,7),(8,10),(9,10),(10,10)]:
            value=Lead("a@b","manual",score)
            self.assertEqual(flag_high_score(value).score,expected)
            self.assertEqual(value.score,score)
        rows=[{"version":2,"contact":{"email":"A@B"},"ranking":{"score":9}}]
        self.assertEqual(fetch_leads(lambda:rows,adapt_webhook,lambda lead:lead),[Lead("a@b","webhook",9)])


if __name__=="__main__": unittest.main()
