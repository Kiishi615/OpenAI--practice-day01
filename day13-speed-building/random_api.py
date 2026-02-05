import requests, streamlit as st
import json

st.title("🪇 Random User Generator")
st.write("Generate Fake users for testing")

gender = st.selectbox("Pick a gender:", ["male", "female", "any"])
count = st.slider("How many random people do you want: " , 1, 10, 5)

if st.button("Generate User(s)"):
    url = "https://randomuser.me/api/"
    params = {
        "results": count,
        "gender" : gender if gender !="any" else " ",
        "format": "json"
    }
    try: 
        r = requests.get(url=url, params=params)

        data = r.json()

        for person in data["results"]:
            name = f"{person['name']['title'] +'. ' + person['name']['first']+ ' ' +person['name']['last']}"
            age = f"{person['dob']['age']}\n"

            st.success(f"{name} - {age}")
    except requests.Timeout :
        print("Request timeout")
    except requests.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
    except requests.RequestException as e:
        print(f"Network error: {e}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON decode")


