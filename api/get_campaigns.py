
"""This example illustrates how to get all campaigns.
To add campaigns, run add_campaigns.py.
"""


import argparse
import sys
import os

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

refresh_token = 'this will be dynamic'


def main(client, customer_id):
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT 
            campaign.id, 
            campaign.name, 
            campaign.campaign_budget, 
            campaign.bidding_strategy, 
            campaign.status, 
            campaign.start_date, 
            segments.device, 
            metrics.average_cpc, 
            metrics.average_cpm, 
            metrics.clicks, 
            metrics.ctr
        FROM campaign
        ORDER BY campaign.id"""

    # Issues a search request using streaming.
    response = ga_service.search_stream(customer_id=customer_id, query=query)

    for batch in response:
        for row in batch.results:
            print(
                f"Campaign with ID {row.campaign.id} and name "
                f'"{row.campaign.name}" was found. '
                f"Campaign budget is ${(row.campaign_budget.amount_micros)/1000000} "
                # f"Campaign bidding strategy is {row.bidding_strategy.type} "
                # f"Campaign status is {row.campaign.status} "
                f"Campaign start date is {row.campaign.start_date} "
                f"The segments device are {row.segments.device} "
                f"The CPC is ${round((row.metrics.average_cpc/1000000),2)} "
                f"The CPM is ${round((row.metrics.average_cpm/1000000),2)} "
                f"The campaign got {row.metrics.clicks} clicks "
                f"The campaign has a CTR of {round(row.metrics.ctr, 2)} "

            )


if __name__ == "__main__":
    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    # I had to create an object called yaml_path to store the yaml file path,
    # and added that object as a parameter when calling GoogleAdsClient service.
    # yaml_path = "/Applications/Python 3.9/google_ads/ads_web_app/fran_ads/backend/backend/google_ads/google-ads.yaml"
    # googleads_client = GoogleAdsClient.load_from_storage(yaml_path, version="v8")

    # Configurations
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DEVELOPER_TOKEN = os.environ.get("GOOGLE_DEVELOPER_TOKEN", None)
    GOOGLE_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_LOGIN_CUSTOMER_ID", None)

    # Configure using dict (the refresh token will be a dynamic value)
    credentials = {
    "developer_token": GOOGLE_DEVELOPER_TOKEN,
    "refresh_token": refresh_token,
    "client_id": GOOGLE_CLIENT_ID,
    "client_secret": GOOGLE_CLIENT_SECRET,
    "login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID}

    googleads_client = GoogleAdsClient.load_from_dict(credentials)

    parser = argparse.ArgumentParser(
        description="Lists all campaigns for specified customer."
    )
    # The following argument(s) should be provided to run the example.
    parser.add_argument(
        "-c",
        "--customer_id",
        type=str,
        required=True,
        help="The Google Ads customer ID.",
    )
    args = parser.parse_args()

    try:
        main(googleads_client, args.customer_id)
    except GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print(f'	Error with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)
