import os
import sys
import json


from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def search_terms_report(refresh_token, customer_id, campaign_id, date_range):

    try:
        # Configurations
        GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
        GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
        GOOGLE_DEVELOPER_TOKEN = os.environ.get("GOOGLE_DEVELOPER_TOKEN", None)
        # GOOGLE_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_LOGIN_CUSTOMER_ID", None)

        # Configure using dict (the refresh token will be a dynamic value)
        credentials = {
        "developer_token": GOOGLE_DEVELOPER_TOKEN,
        "refresh_token": refresh_token,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        # "login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID,
        "linked_customer_id": customer_id,
        "use_proto_plus": True}

        googleads_client = GoogleAdsClient.load_from_dict(credentials)

        ga_service = googleads_client.get_service("GoogleAdsService")

        # date selected by user on UI
        date_range = date_range

        if date_range == "ALL_TIME":
            query = (f'''
                SELECT campaign.id, campaign.name, 
                metrics.impressions, metrics.clicks,
                metrics.cost_micros,
                smart_campaign_search_term_view.search_term
                FROM smart_campaign_search_term_view 
                WHERE campaign.id = {campaign_id} 
                ORDER BY metrics.clicks DESC
                LIMIT 10''')
        else: query = (f'''
                SELECT campaign.id, campaign.name, 
                metrics.impressions, metrics.clicks,
                metrics.cost_micros, 
                smart_campaign_search_term_view.search_term
                FROM smart_campaign_search_term_view 
                WHERE campaign.id = {campaign_id} 
                AND segments.date DURING {date_range}
                ORDER BY metrics.clicks DESC
                LIMIT 10''')

        # Issues a search request using streaming.
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        # to store the search terms report data
        search_terms_report = []

        for batch in response:
            for row in batch.results:
                data_search_terms = {}
                data_search_terms["search_term"] = row.smart_campaign_search_term_view.search_term
                print(data_search_terms["search_term"])
                data_search_terms["search_term_impressions"] = row.metrics.impressions
                data_search_terms["search_term_clicks"] = row.metrics.clicks
                data_search_terms["search_term_cost"] = round((row.metrics.cost_micros/1000000), 2)
                search_terms_report.append(data_search_terms)


        print(search_terms_report)
        json.dumps(search_terms_report)
        return search_terms_report

    except GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)