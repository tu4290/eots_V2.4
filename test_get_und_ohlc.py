# test_get_chain_params.py
import os
import json
import requests # For handling HTTP exceptions
from convexlib.api import ConvexApi # Assuming convexlib is installed and in the path
from dotenv import load_dotenv
from typing import List, Dict, Any

# --- Configuration ---
# Root symbol for the option chain (e.g., "SPY", "AAPL")
ROOT_SYMBOL_TO_TEST = "/es:xcme"

# Expirations to request:
# - Can be a list of integers for the Nth upcoming expirations (e.g., [0, 1, 2] for the first 3)
# - Can be a list of specific date strings "YYYY-MM-DD" (e.g., ["2024-06-21", "2024-07-19"])
# - Can be None to fetch all available (may result in a very large response)
EXPS_TO_REQUEST: List[Any] = [0, 1] # Fetch the first 2 available expirations

# Strike range:
# - Percentage around the money (e.g., 0.10 for 10% OTM/ITM)
# - Can be None to fetch all strikes for the selected expirations (may result in a very large response)
STRIKE_RANGE: float | None = 0.05 # 5% around the money

# PARAMETERS TO REQUEST FOR OPTION CHAIN DATA
CHAIN_PARAMS_TO_REQUEST: List[str] = [
    "price",                # Option's last price
    "volatility",           # Option's Implied Volatility
    "multiplier",           # Contract multiplier
    "oi",                   # Option's Open Interest
    "delta",                # Core Greek
    "gamma",                # Core Greek
    "theta",                # Core Greek
    "vega",                 # Core Greek
    "vanna",                # Core Greek
    "vomma",                # Core Greek
    "charm",                # Core Greek
    # "rho",                # Optional Core Greek
    "dxoi",                 # Delta * OI
    "gxoi",                 # Gamma * OI
    "vxoi",                 # Vega * OI
    "txoi",                 # Theta * OI
    "vannaxoi",             # Vanna * OI
    "vommaxoi",             # Vomma * OI
    "charmxoi",             # Charm * OI
    "dxvolm",               # Delta * Volume
    "gxvolm",               # Gamma * Volume
    "vxvolm",               # Vega * Volume
    "txvolm",               # Theta * Volume
    "vannaxvolm",           # Vanna * Volume
    "vommaxvolm",           # Vomma * Volume
    "charmxvolm",           # Charm * Volume
    "value_bs",             # Net (Buy Value - Sell Value) per contract
    "volm_bs",              # Net (Buy Volume - Sell Volume) per contract
    "deltas_buy",           # Sum of Delta from customer BUYS
    "deltas_sell",          # Sum of Delta from customer SELLS
    "gammas_buy",           # Sum of Gamma from customer BUYS
    "gammas_sell",          # Sum of Gamma from customer SELLS
    "vegas_buy",            # Sum of Vega from customer BUYS
    "vegas_sell",           # Sum of Vega from customer SELLS
    "thetas_buy",           # Sum of Theta from customer BUYS
    "thetas_sell",          # Sum of Theta from customer SELLS
    "valuebs_5m",           # Rolling Net Value (5 min)
    "volmbs_5m",            # Rolling Net Volume (5 min)
    "valuebs_15m",          # Rolling Net Value (15 min)
    "volmbs_15m",           # Rolling Net Volume (15 min)
    "valuebs_30m",          # Rolling Net Value (30 min)
    "volmbs_30m",           # Rolling Net Volume (30 min)
    "valuebs_60m",          # Rolling Net Value (60 min)
    "volmbs_60m",           # Rolling Net Volume (60 min)
]

# --- Load Environment Variables ---
project_root = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(project_root, ".env")

if not os.path.exists(dotenv_path):
    parent_dir = os.path.dirname(project_root)
    dotenv_path_alt = os.path.join(parent_dir, ".env")
    if os.path.exists(dotenv_path_alt):
        dotenv_path = dotenv_path_alt
    else:
        grandparent_dir = os.path.dirname(parent_dir)
        dotenv_path_grandparent = os.path.join(grandparent_dir, ".env")
        if os.path.exists(dotenv_path_grandparent):
            dotenv_path = dotenv_path_grandparent

if os.path.exists(dotenv_path):
    print(f"Loading .env file from: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path, verbose=True, override=True)
else:
    print(f"Warning: .env file not found at expected locations. Relying on system environment variables if set.")

api_email = os.getenv("CONVEX_EMAIL")
api_password = os.getenv("CONVEX_PASSWORD")

if not api_email or not api_password:
    print("Error: CONVEX_EMAIL or CONVEX_PASSWORD not found in environment variables or .env file.")
    exit(1)

# --- Main Test Logic ---
def main_test():
    """
    Main function to test fetching option chain data from ConvexAPI.
    """
    print(f"Attempting to connect to ConvexAPI with user: {api_email[:3]}***")
    try:
        api = ConvexApi(email=api_email, password=api_password)
        print("Successfully connected to ConvexAPI.")
    except NameError:
        print("ERROR: ConvexApi class not found. Make sure it's imported or defined correctly.")
        return
    except Exception as e:
        print(f"Error connecting to ConvexAPI: {e}")
        return

    print(f"\nFetching option chain for symbol: {ROOT_SYMBOL_TO_TEST}")
    print(f"Requesting parameters ({len(CHAIN_PARAMS_TO_REQUEST)} total): {CHAIN_PARAMS_TO_REQUEST}")
    print(f"Expirations: {EXPS_TO_REQUEST}")
    print(f"Strike Range: {STRIKE_RANGE if STRIKE_RANGE is not None else 'All'}")

    # Test get_chain
    try:
        print(f"\n--- Testing get_chain for {ROOT_SYMBOL_TO_TEST} ---")
        chain_data_response = api.get_chain(
            root=ROOT_SYMBOL_TO_TEST,
            params=CHAIN_PARAMS_TO_REQUEST,
            exps=EXPS_TO_REQUEST,
            rng=STRIKE_RANGE
        )
        print("\nRaw API Response (get_chain):")
        print(json.dumps(chain_data_response, indent=2))

        # Basic validation of get_chain response structure
        if not isinstance(chain_data_response, dict) or "data" not in chain_data_response:
            print("\nWARNING: get_chain response format is unexpected (missing 'data' field or not a dictionary).")
        elif not isinstance(chain_data_response["data"], list) or not chain_data_response["data"]:
            print("\nWARNING: get_chain 'data' field is not a list or is empty.")
        else:
            # Further checks could be added here if a more detailed structure is known
            print("\nSUCCESS: get_chain returned a response with 'data'. Further processing would depend on its structure.")


    except requests.exceptions.HTTPError as e_http:
        print(f"\nHTTPError occurred during get_chain: {e_http.response.status_code} - {e_http.response.reason}")
        print("Response body (if any):")
        try:
            error_details = e_http.response.json()
            print(json.dumps(error_details, indent=2))
        except json.JSONDecodeError:
            print(e_http.response.text)
        print("\nThis usually means one or more requested parameters are invalid for 'get_chain',")
        print("the symbol is incorrect, expirations/range are problematic, or an auth issue.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during get_chain: {e}")
        import traceback
        traceback.print_exc()

    # Test get_chain_as_rows
    try:
        print(f"\n--- Testing get_chain_as_rows for {ROOT_SYMBOL_TO_TEST} ---")
        chain_rows_response = api.get_chain_as_rows(
            root=ROOT_SYMBOL_TO_TEST,
            params=CHAIN_PARAMS_TO_REQUEST,
            exps=EXPS_TO_REQUEST,
            rng=STRIKE_RANGE
        )
        print("\nAPI Response (get_chain_as_rows):")
        if isinstance(chain_rows_response, list):
            if not chain_rows_response:
                print("  (No rows returned by get_chain_as_rows)")
            else:
                # Create header for the rows
                header = ["symbol", "expiration", "strike", "kind"] + CHAIN_PARAMS_TO_REQUEST
                print("  " + ", ".join(map(str, header))) # Print header
                for i, row in enumerate(chain_rows_response):
                    if i < 20: # Print first 20 rows to avoid flooding console
                        print(f"  Row {i+1}: {row}")
                    elif i == 20:
                        print(f"  (... and {len(chain_rows_response) - 20} more rows ...)")
                print(f"\nSUCCESS: get_chain_as_rows returned {len(chain_rows_response)} rows.")
        else:
            print("\nWARNING: get_chain_as_rows did not return a list as expected.")
            print(f"Received: {type(chain_rows_response)} - {chain_rows_response}")


    except requests.exceptions.HTTPError as e_http:
        # This might be redundant if get_chain_as_rows calls get_chain internally and get_chain already handled it.
        # However, keeping it in case get_chain_as_rows has its own potential for HTTP errors or different handling.
        print(f"\nHTTPError occurred during get_chain_as_rows: {e_http.response.status_code} - {e_http.response.reason}")
        print("Response body (if any):")
        try:
            error_details = e_http.response.json()
            print(json.dumps(error_details, indent=2))
        except json.JSONDecodeError:
            print(e_http.response.text)
    except Exception as e:
        print(f"\nAn unexpected error occurred during get_chain_as_rows: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main_test()
