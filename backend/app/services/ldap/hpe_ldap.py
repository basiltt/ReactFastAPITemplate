import asyncio
import socket
import ssl
from typing import Union, List

import ldap3
from _socket import timeout, gaierror
from fastapi import HTTPException
from starlette import status

from backend.app.services.ldap.helpers import aioldap
from backend.app.services.ldap.helpers.aioldap import LDAPBindException

# Defining the constants
LDAP_SERVER = "hpe-pro-ods-ed.infra.hpecorp.net"
LDAP_PORT = 636
SEARCH_BASE = "ou=People,o=hp.com"

LDAP_AUTH_SERVER = "ad-hpqcorp-glb-appsint.glb1.hpecorp.net"
LDAP_AUTH_PORT = 3269

# Static Strings
AD_USER_NOT_FOUND_ERROR = "User not found in Active Directory"
LDAP_UNKNOWN_ERROR = "LDAP Unknown Error"
INVALID_CREDENTIALS = "Invalid Credentials"
PARAMETER_MISSING_ERROR = "Required parameter missing"
PDL_MEMBERS_SEARCH_BASE = (
    "OU=Managed Groups,OU=Accounts,DC=asiapacific,DC=cpqcorp,DC=net"
)
SUPPORT_PDL = "rpa_fin_support_team@hpe.com"


async def get_ldap_user(
    email: str = None, nt_user: str = None, raise_exception_on_not_found: bool = True
) -> Union[dict, None]:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.set_ciphers("DEFAULT")
    ciphers = "ALL"

    tls = ldap3.Tls(ciphers=ciphers, validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS)
    server = aioldap.Server(
        host=LDAP_SERVER, port=LDAP_PORT, use_ssl=True, ssl_context=ssl_context, tls=tls
    )
    conn = aioldap.LDAPConnection(server)
    await conn.bind()
    search_string = ""
    if email:
        search_string = f"(uid={email})"
    elif nt_user:
        nt_user_split = nt_user.split("\\")
        if len(nt_user_split) > 1:
            nt_user_modified = f"{nt_user_split[0].upper()}:{nt_user_split[1].lower()}"
        else:
            nt_user_modified = nt_user
        search_string = f"(ntUserDomainId={nt_user_modified})"
    else:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=PARAMETER_MISSING_ERROR,
        )
    result = await conn.search(
        search_base=SEARCH_BASE, search_filter=search_string, attributes="*"
    )
    if len(result["entries"]) < 1:
        if raise_exception_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=AD_USER_NOT_FOUND_ERROR,
            )
        else:
            return None
    try:
        nt_user = (
            result["entries"][0]["raw_attributes"]["ntUserDomainId"][0]
            .decode("utf-8")
            .replace(":", "\\")
        )
        email_id = result["entries"][0]["raw_attributes"]["uid"][0].decode("utf-8")
        user_domain = (
            result["entries"][0]["raw_attributes"]["krbName"][0]
            .decode("utf-8")
            .split("@")[1]
            .lower()
        )
        full_name = (
            result["entries"][0]["raw_attributes"]["cn"][0]
            .decode("utf-8")
            .replace(":", "\\")
        )
        employee_id_tuple = (
            (
                result["entries"][0]["raw_attributes"]["employeeNumber"][0].decode(
                    "utf-8"
                )
            ),
        )
        if "co" in result["entries"][0]["raw_attributes"]:
            country = (
                result["entries"][0]["raw_attributes"]["co"][0]
                .decode("utf-8")
                .replace(":", "\\")
            )
        else:
            country = ""
        manager = (
            result["entries"][0]["raw_attributes"]["manager"][0]
            .decode("utf-8")
            .replace("uid=", "")
            .replace(",ou=People,o=hp.com", "")
        )
        cost_center = result["entries"][0]["raw_attributes"]["hpLHCostCenter"][
            0
        ].decode("utf-8")
        if "hpPictureOneHpURI" in result["entries"][0]["raw_attributes"]:
            image_url = result["entries"][0]["raw_attributes"]["hpPictureOneHpURI"][
                0
            ].decode("utf-8")
            if image_url:
                image_url = image_url.replace("http", "https")
        else:
            image_url = ""
        return {
            "domain_id": nt_user,
            "email": email_id,
            "user_domain": user_domain,
            "name": full_name,
            "employee_id": employee_id_tuple[0],
            "country": country,
            "manager_email": manager,
            "cost_center": cost_center,
            "profile_picture": image_url,
        }
    except Exception as e:
        print(f"Error --> {e.args}")
        raise HTTPException(
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            detail=LDAP_UNKNOWN_ERROR,
        )


async def get_ldap_users(users: List[str]) -> List[dict]:
    ldap_users = []
    for user in users:
        ldap_user = await get_ldap_user(email=user)
        ldap_users.append(ldap_user)
    return ldap_users


async def validate_ldap_credentials(username: str, password: str) -> bool:
    """
    Method to validate ldap credentials
    :param username: username as string
    :param password: password as string
    :return: result as boolean
    """
    server = aioldap.Server(host=LDAP_AUTH_SERVER, port=LDAP_AUTH_PORT, use_ssl=True)
    conn = aioldap.LDAPConnection(server)
    try:
        await conn.bind(username, password)
        return True
    except LDAPBindException:
        return False
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            detail=LDAP_UNKNOWN_ERROR,
        )


async def validate_hpe_connectivity() -> bool:
    """
    Method to do quick connectivity test
    :return: connectivity test result as boolean
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((LDAP_AUTH_SERVER, LDAP_AUTH_PORT))
        return True
    except (timeout, gaierror):
        return False


async def get_pdl_members(pdl: str, username: str, password: str) -> list:
    """
    Method to get PDL members
    :return: list of PDL members
    """
    server = aioldap.Server(host=LDAP_AUTH_SERVER, port=LDAP_AUTH_PORT, use_ssl=True)
    conn = aioldap.LDAPConnection(server)
    try:
        await conn.bind(username, password)
    except LDAPBindException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            detail=LDAP_UNKNOWN_ERROR,
        )
    result = await conn.search(
        search_base=PDL_MEMBERS_SEARCH_BASE,
        search_filter=f"(CN={pdl})",
        search_scope=ldap3.SUBTREE,
        attributes=ldap3.ALL_ATTRIBUTES,
    )
    members_raw = result["entries"][0]["raw_attributes"]["member"]
    members = []
    for member in members_raw:
        member = member.decode("utf-8")
        member = member.split(",")[0].split("=")[1]
        members.append(member)
    return members
