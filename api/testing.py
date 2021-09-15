import os
import sys
from uuid import uuid4
import json

from google.ads.googleads.client import GoogleAdsClient
# from google.ads.googleads.errors import GoogleAdsException
# from google.api_core import protobuf_helpers


# customer_id = str(4037974191) # billing set up    | account created via api
# # customer_id = str(4597538560) # no billing        | account created via api
customer_id = str(2916870939) # billing set up      | account created via ui


# Configurations
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DEVELOPER_TOKEN = os.environ.get("GOOGLE_DEVELOPER_TOKEN", None)
GOOGLE_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_LOGIN_CUSTOMER_ID", None)
GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)

# Configure using dict (the refresh token will be a dynamic value)
credentials = {
"developer_token": GOOGLE_DEVELOPER_TOKEN,
"refresh_token": GOOGLE_REFRESH_TOKEN,
"client_id": GOOGLE_CLIENT_ID,
"client_secret": GOOGLE_CLIENT_SECRET,
"login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID}

client = GoogleAdsClient.load_from_dict(credentials)




# '''
# Check if customer id has set up billing
# '''

# # customer_id = str(4037974191) # billing set up    | account created via api
# # customer_id = str(4597538560) # no billing        | account created via api
# customer_id = str(2916870939) # billing set up      | account created via ui

# ga_service = client.get_service("GoogleAdsService")

# query = """
#     SELECT
#         billing_setup.id,
#         billing_setup.status,
#         billing_setup.payments_account,
#         billing_setup.payments_account_info.payments_account_id,
#         billing_setup.payments_account_info.payments_account_name,
#         billing_setup.payments_account_info.payments_profile_id,
#         billing_setup.payments_account_info.payments_profile_name,
#         billing_setup.payments_account_info.secondary_payments_profile_id
#     FROM billing_setup"""

# response = ga_service.search_stream(customer_id=customer_id, query=query)

# print("Found the following billing setup results:")
# for batch in response:
#     for row in batch.results:
#         billing_setup = row.billing_setup
#         pai = billing_setup.payments_account_info

#         if pai.secondary_payments_profile_id:
#             secondary_payments_profile_id = (
#                 pai.secondary_payments_profile_id
#             )
#         else:
#             secondary_payments_profile_id = "None"

#         print(
#             f"Billing setup with ID {billing_setup.id}, "
#             f'status "{billing_setup.status.name}", '
#             f'payments_account "{billing_setup.payments_account}" '
#             f"payments_account_id {pai.payments_account_id}, "
#             f'payments_account_name "{pai.payments_account_name}", '
#             f"payments_profile_id {pai.payments_profile_id}, "
#             f'payments_profile_name "{pai.payments_profile_name}", '
#             "secondary_payments_profile_id "
#             f"{secondary_payments_profile_id}."
#         )

# try:
#     billing_status = billing_setup.status.name
# except NameError:
#     billing_status = "no billing"

# print('billing_status:')
# print(billing_status)


# '''
# Link accounts
# '''
# # This example assumes that the same credentials will work for both
# # customers, but that may not be the case. If you need to use different
# # credentials for each customer, then you may either update the client
# # configuration or instantiate two clients, where at least one points to
# # a specific configuration file so that both clients don't read the same
# # file located in the $HOME dir.
# customer_client_link_service = client.get_service(
#     "CustomerClientLinkService"
# )

# # Extend an invitation to the client while authenticating as the manager.
# client_link_operation = client.get_type("CustomerClientLinkOperation")
# client_link = client_link_operation.create
# client_link.client_customer = customer_client_link_service.customer_path(customer_id)
# client_link.status = client.enums.ManagerLinkStatusEnum.PENDING

# response = customer_client_link_service.mutate_customer_client_link(
#     customer_id=GOOGLE_LOGIN_CUSTOMER_ID, operation=client_link_operation
# )
# resource_name = response.results[0].resource_name

# print(
#     f'Extended an invitation from customer "{GOOGLE_LOGIN_CUSTOMER_ID}" to '
#     f'customer "{customer_id}" with client link resource_name '
#     f'"{resource_name}"'
# )

# # Find the manager_link_id of the link we just created, so we can construct
# # the resource name for the link from the client side. Note that since we
# # are filtering by resource_name, a unique identifier, only one
# # customer_client_link resource will be returned in the response
# query = f'''
#     SELECT
#         customer_client_link.manager_link_id
#     FROM
#         customer_client_link
#     WHERE
#         customer_client_link.resource_name = "{resource_name}"'''

# ga_service = client.get_service("GoogleAdsService")

# try:
#     response = ga_service.search(
#         customer_id=GOOGLE_LOGIN_CUSTOMER_ID, query=query
#     )
#     # Since the googleads_service.search method returns an iterator we need
#     # to initialize an iteration in order to retrieve results, even though
#     # we know the query will only return a single row.
#     for row in response.result:
#         manager_link_id = row.customer_client_link.manager_link_id
# except GoogleAdsException as ex:
#     print(
#         f'Request with ID "{ex.request_id}" failed with status '
#         f'"{ex.error.code().name}" and includes the following errors:'
#     )
#     for error in ex.failure.errors:
#         print(f'\tError with message "{error.message}".')
#         if error.location:
#             for field_path_element in error.location.field_path_elements:
#                 print(f"\t\tOn field: {field_path_element.field_name}")
#     sys.exit(1)

# customer_manager_link_service = client.get_service(
#     "CustomerManagerLinkService"
# )
# manager_link_operation = client.get_type("CustomerManagerLinkOperation")
# manager_link = manager_link_operation.update
# manager_link.resource_name = (
#     customer_manager_link_service.customer_manager_link_path(
#         customer_id,
#         GOOGLE_LOGIN_CUSTOMER_ID,
#         manager_link_id,
#     )
# )

# manager_link.status = client.enums.ManagerLinkStatusEnum.ACTIVE
# client.copy_from(
#     manager_link_operation.update_mask,
#     protobuf_helpers.field_mask(None, manager_link._pb),
# )

# response = customer_manager_link_service.mutate_customer_manager_link(
#     customer_id=GOOGLE_LOGIN_CUSTOMER_ID, operations=[manager_link_operation]
# )
# print(
#     "Client accepted invitation with resource_name: "
#     f'"{response.results[0].resource_name}"'
# )