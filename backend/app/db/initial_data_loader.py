# # Load initial data to database
# from typing import Union
#
# from loguru import logger
# from sqlmodel import Session
# from sqlmodel.ext.asyncio.session import AsyncSession
#
# from backend.app.api.routes.access.helpers.access_helper import add_roles
# from backend.app.api.routes.admin.helpers.admin_helper import add_admin
# from backend.app.api.routes.sfdc.helpers.sfdc_helper import add_sfdc_product_mapping
# from backend.app.models.access.access_request import CreateRoleRequest
#
# ADMINS = ["basil.tt@hpe.com", "arun.benitto@hpe.com"]
# SOLUTION_FAMILY_MAPPINGS = [
#     {"solution_family": "Orchestration", "product_solution_family": "ORC"},
#     {"solution_family": "Mobile Core & 5G", "product_solution_family": "M5G"},
#     {"solution_family": "Assurance", "product_solution_family": "ASR"},
#     {"solution_family": "Digital", "product_solution_family": "DIG"},
#     {"solution_family": "Fulfillment and RI", "product_solution_family": "FRI"},
#     {"solution_family": "Digital Identity", "product_solution_family": "DID"},
# ]
# ROLES = [
#     "NPI",
#     "CC",
#     "Solution Architect",
#     "Process Owner",
#     "Support",
#     "Admin",
#     "Product Manager",
#     "Release Manager",
#     "Q2C PDM CPL Admin"
# ]
#
#
# async def load_initial_data_to_db(
#     session: Union[AsyncSession, Session],
#     info=logger.info("Loading initial data to database"),
# ):
#     """Load initial data to database."""
#
#     for admin in ADMINS:
#         await add_admin(admin, session, raise_exception_on_found=False)
#
#     for solution_family_mapping in SOLUTION_FAMILY_MAPPINGS:
#         await add_sfdc_product_mapping(
#             created_by="basil.tt@hpe.com",
#             sfdc_solution_family=solution_family_mapping.get("solution_family"),
#             product_solution_family=solution_family_mapping.get(
#                 "product_solution_family"
#             ),
#             session=session,
#             raise_exception_on_found=False,
#         )
#     for role in ROLES:
#         # role: CreateRoleRequest = CreateRoleRequest(role=role, created_by=ADMINS[0])
#         # noinspection PyTypeChecker
#         await add_roles(
#             role=role,
#             created_by=ADMINS[0],
#             session=session,
#             raise_exception_on_found=False,
#         )
#
#     logger.info("Initial data loaded to database")
