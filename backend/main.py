import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
import pandas as pd
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse,JSONResponse

qty = 1
groups_of_valves = []
fertikit = False
ec_ph = False
weather_station = False

app = FastAPI()

# ------------------ SYSTEM PARTS ------------------


# ------------------ SYSTEM SELECTION ------------------

def choose_system(field_area: float) -> str:
    if field_area < 40:
        return "multicable"
    elif field_area <= 200:
        return "singlenet"
    else:
        return "radionet"

# ------------------ PARTS GENERATION ------------------

def generate_parts(system_name: str, total_valves: str, fertikit: bool, ec_ph: bool, weather_station: bool):
    parts = [p.copy() for p in SYSTEM_PARTS[system_name]]
    rtu2x2 = 0
    rtu4x4 = 0
    rtu2x2_radio = 0
    rtu_expandable = 0
    expansion_board = 0
    solar_panel_qty = 0

    if system_name == "multicable":
        valves = 0
        relay = 1
        for v in total_valves:  
          valves = valves + v
          for p in parts:
                if valves > 16 and p.get("part")=="16-DO RELAY":
                    relay = relay+1
                    p["Qty"] = relay

                if valves > 32 and p.get("part")=="16-DO RELAY":
                    relay = relay+2
                    p["Qty"] = relay
                    
                if valves > 48 and p.get("part")=="16-DO RELAY":
                    relay = relay+3
                    p["Qty"] = relay
                if valves > 64 and p.get("part")=="16-DO RELAY":
                    relay = relay+4
                    p["Qty"] = relay

                if valves > 80 and p.get("part")=="16-DO RELAY":
                    return {"error": "Sorry you reached the maximum number of valves fo rthe system."}

    if system_name == "singlenet":     
        for v in total_valves:  
          for p in parts:
              if v <= 2 and p.get("part")=="RTU 2x2":
                rtu2x2 = rtu2x2+1
                p["Qty"] = rtu2x2
              if v > 2 and v <= 4 and p.get("part")=="RTU 4x4":
                rtu4x4 = rtu4x4+1
                p["Qty"] = rtu4x4
              if v > 4 and v <= 6 and p.get("part")=="RTU 4x4":
                rtu4x4 = rtu4x4+1
                p["Qty"] = rtu4x4
              if v > 4 and v <= 6 and p.get("part")=="RTU 2x2":
                rtu2x2 = rtu2x2+1
                p["Qty"] = rtu2x2
              if v > 6 and p.get("part")=="RTU 4x4":
                rtu4x4 = rtu4x4+2
                p["Qty"] = rtu4x4
        print(fertikit)


        
    if system_name == "radionet":
        
        for r in range(len(total_valves)):
          solar_panel_qty = solar_panel_qty+1
            
        for v in total_valves:  
          for p in parts:
              if v <= 2 and p.get("part")=="RTU 2x2":
                rtu2x2_radio = rtu2x2_radio+1
                p["Qty"] = rtu2x2_radio
              if v > 2 and v <= 3 and p.get("part")=="RTU Expandable":
                rtu_expandable = rtu_expandable+1
                expansion_board = expansion_board+1
                p["Qty"] = rtu_expandable
              if v > 3 and v <= 5 and p.get("part")=="RTU Expandable":
                rtu_expandable = rtu_expandable+1
                expansion_board = expansion_board+2
                p["Qty"] = rtu_expandable
              if v > 5 and v <= 7 and p.get("part")=="RTU Expandable":
                rtu_expandable = rtu_expandable+1
                expansion_board = expansion_board+3
                p["Qty"] = rtu_expandable
              if v > 7 and v <= 9 and p.get("part")=="RTU Expandable":
                rtu_expandable = rtu_expandable+1
                expansion_board = expansion_board+4
                p["Qty"] = rtu_expandable
              if p.get("part")== "Expans. Board":
                p["Qty"] = expansion_board
              if p.get("part")== "RADIONET SOLAR PANEL":
                    p["Qty"] = solar_panel_qty
    # Optional add-ons
    if fertikit:
                parts.append( {"part": "Triac", "SN": "74743-000099","name": "GS-MAX 8 TRIAC","Qty": 1},)
    if ec_ph:
                parts.append({"part": "4 AI", "SN": "74743-000100","name": "GS-MAX 4 AI WITH ADAPTOR","Qty": 1},)
    if weather_station:
                parts.append({"part": "Weather station", "SN": "74730-000050","name": "Davis Weather Station","Qty": 1},)
        
    return parts
# ------------------ EXCEL EXPORT ------------------

def export_system_excel(project_name: str, system_name: str, parts, fertikit: bool, ec_ph: bool, weather_station: bool):
    summary = pd.DataFrame({
        "Parameter": ["System", "Fertikit", "EC/PH", "Weather Station"],
        "Value": [
            system_name,
            "Yes" if fertikit else "No",
            "Yes" if ec_ph else "No",
            "Yes" if weather_station else "No",
        ],
    })
    parts_df = pd.DataFrame(parts, columns=["part", "SN", "name", "Qty"])

    with pd.ExcelWriter(f"{system_name}_irrigation_system.xlsx") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        parts_df.to_excel(writer, sheet_name="Parts List", index=False)

    parts_df = pd.DataFrame(parts)

    filename = f"{project_name}_design.xlsx"
    with pd.ExcelWriter(filename) as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        parts_df.to_excel(writer, sheet_name="Parts", index=False)

    return filename

# ------------------ EXCEL GENERATION ENDPOINT ------------------

@app.post("/design_system/")
def design_system(
    project_name: str = Form(...),
    system_type: str = Form(...),
    total_valves: str = Form(...),
    fertikit: bool = Form(...),
    ec_ph: bool = Form(...),
    weather_station: bool = Form(...)
):
    valves_groups = create_valves_groups(total_valves)
    system = system_type.lower()
    parts = generate_parts(system, valves_groups, fertikit, ec_ph, weather_station)
    filename = export_system_excel(project_name,system, parts,fertikit, ec_ph, weather_station)
    return FileResponse(filename, filename=filename)



# CHAT ENDPOINT
# -------------------------------------------------------
@app.post("/chat/")
def chat(message: str = Form(...)):
    intent = predict_intent(message)

    if intent == "greeting":
        return JSONResponse({"reply": "Hello! How can I help you today?"})

    if intent == "goodbye":
        return JSONResponse({"reply": "Goodbye! Take care."})

    if intent == "knowledge_query":
        passage = retrieve_relevant_passage(message)
        return JSONResponse({"reply": passage[0][0]})

    if intent in ["singlenet", "radionet", "multicable"]:
        return JSONResponse({"reply": f"{intent.capitalize()} is a great choice. How many valves do you have?"})

    if intent == "export_excel":
        return JSONResponse({"reply": "Please provide field_area and total_valves to generate the Excel file."})

    return JSONResponse({"reply": "I'm not sure I understand yet, but I'm learning."})

# -------------------------------------------------------



# ---------------- Knowledge base ----------------
with open(r"\knowledge.txt", "r") as f:
    documents = [line.strip() for line in f if line.strip()]

vectorizer_docs = TfidfVectorizer()
doc_vectors = vectorizer_docs.fit_transform(documents)

def retrieve_relevant_passage(query, top_k=1):
    query_vec = vectorizer_docs.transform([query])
    sims = cosine_similarity(query_vec, doc_vectors).flatten()
    top_indices = sims.argsort()[::-1][:top_k]
    return [(documents[i], sims[i]) for i in top_indices]

# ---------------- Parts DB ----------------
SYSTEM_PARTS = {
    "fertikit": [
        {"part": "Triac", "SN": "74743-000099","name": "GS-MAX 8 TRIAC","Qty": qty},
    ],
    "ec/ph": [
        {"part": "4 AI", "SN": "74743-000100","name": "GS-MAX 4 AI WITH ADAPTOR","Qty": qty},
    ],
    "weather-station": [
        {"part": "Weather station", "SN": "74730-000050","name": "Davis Weather Station","Qty": qty},
    ],
    "singlenet": [
        {"part": "Controller", "SN": "74702-000069","name": "GS Max With Double Door Controller","Qty": qty},
        {"part": "RS232", "SN": "74743-000014","name": "RS232 SERIAL PORT","Qty": qty},
        {"part": "RS485", "SN": "74743-000017","name": "RS485 SERIAL PORT","Qty": qty},
        {"part": "Host", "SN": "00035-00176","name": "Singlenet Host","Qty": qty},
        {"part": "RTU 2x2", "SN": "74340-01490","name": "SingleNet RTU 2x2","Qty": qty - 1},
        {"part": "RTU 4x4", "SN": "74340-015000","name": "SingleNet RTU 4x4","Qty": qty - 1},
    ],
    "radionet": [
        {"part": "Controller", "SN": "74702-000069","name": "GS Max With Double Door Controller","Qty": qty},
        {"part": "RS232", "SN": "74743-000014","name": "RS232 SERIAL PORT","Qty": qty},
        {"part": "RS485", "SN": "74743-000017","name": "RS485 SERIAL PORT","Qty": qty},
        {"part": "Host and Base", "SN": "74360-007600","name": "RadioNet HOST + BASE","Qty": qty},
        {"part": "RTU 2x2", "SN": "74330-012195","name": "RadioNet RTU 2DI-2DO","Qty": qty-1},
        {"part": "RTU Expandable", "SN": "74330-012200","name": "RadioNet RTU 2DI-1DO Expandable","Qty": qty-1},
        {"part": "RADIONET SOLAR PANEL", "SN": "74330-005760","name": "RADIONET SOLAR PANEL KIT 9V-3W","Qty": qty-1},
        {"part": "Expans. Board", "SN": "74330-013140","name": "RadioNet Expansion Board 2DI-2DO","Qty": qty-1},
    ],
    "multicable": [
        {"part": "Controller", "SN": "74702-000069","name": "GS Max With Double Door Controller","Qty": qty},
        {"part": "RS232", "SN": "74743-000014","name": "RS232 SERIAL PORT","Qty": qty},
        {"part": "RS485", "SN": "74743-000017","name": "RS485 SERIAL PORT","Qty": qty},
        {"part": "16-DO RELAY", "SN": "74743-000098","name": "GS-MAX 16 RELAY WITH ADAPTOR","Qty": qty},
    ],
}

# ---------------- Training data ----------------
training_data = [
    ("when should I irrigate", "knowledge_query"),
    ("how does soil type affect irrigation", "knowledge_query"),
    ("tell me about drip irrigation", "knowledge_query"),
    ("What system should I use for a system that is 400m long", "knowledge_query"),
    ("Small system", "knowledge_query"),
    ("when is the best time to irrigate", "knowledge_query"),
    ("how often should I water my crops", "knowledge_query"),
    ("explain irrigation scheduling", "knowledge_query"),
    ("what affects irrigation timing", "knowledge_query"),
    ("how much water do plants need", "knowledge_query"),
    ("Best irrigation", "knowledge_query"),
    ("RadioNet", "radionet"),
    ("RTU", "knowledge_query"),
    ("Small field", "knowledge_query"),
    ("Medium field", "knowledge_query"),
    ("Large field", "knowledge_query"),
    ("Valves", "knowledge_query"),
    ("singleNet", "singlenet"),
    ("multiCable", "multicable"),
    ("radionet", "radionet"),
    ("Netacap", "knowledge_query"),
    ("GS ONE", "knowledge_query"),
    ("GS MAX", "knowledge_query"),
    ("Project is", "project_data"),
    ("I have a small field", "project_data"),
    ("I have a medium field", "project_data"),
    ("I have a large field", "project_data"),
    ("I have a field that is", "project_data"),
    ("group", "create_valves_groups"),
    ("valves group", "create_valves_groups"),
    ("valve groups", "create_valves_groups"),
    ("valve", "create_valves_groups"),
    ("groups of valves", "create_valves_groups"),
    ("groups of", "create_valves_groups"),
    ("create excel file", "export_excel"),
    ("make xls", "export_excel"),
    ("save this to spreadsheet", "export_excel"),
    ("export results", "export_excel"),
    ("generate xls", "export_excel"),
    ("yes", "confirm"),
    ("Yes", "confirm"),
    ("no", "deny"),
    ("hi", "greeting"),
    ("hello there", "greeting"),
    ("good morning", "greeting"),
    ("bye", "goodbye"),
    ("see you later", "goodbye"),
    ("can you help me", "help"),
    ("i need assistance", "help"),
    ("what's the weather", "weather"),
    ("is it raining today", "weather"),
]

texts = [t[0] for t in training_data]
labels = [t[1] for t in training_data]

# ----------- Validation Split -------------
X_train_texts, X_test_texts, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
vectorizer = TfidfVectorizer(ngram_range=(1,2), max_df=0.9, stop_words="english")
X_train = vectorizer.fit_transform(X_train_texts)
X_test = vectorizer.transform(X_test_texts)

clf = LinearSVC()
clf.fit(X_train, y_train)

print("Accuracy: ", clf.score(X_test, y_test))

# ---------------- Intent prediction ----------------
def predict_intent(user_input):
    x = vectorizer.transform([user_input])
    decision_scores = clf.decision_function(x)
    confidence = max(decision_scores[0])
    if confidence < 0.2:
        return "Unknown"
    return clf.predict(x)[0]

def match_intent(user_input):
    text = user_input.lower()
    patterns = [
        (r"(hi|hello|hey)", "greeting"),
        (r"(bye|goodbye|see you)", "goodbye"),
        (r"(help|support)", "help"),
        (r"(weather)", "weather"),
    ]
    for pattern, intent in patterns:
        if re.search(pattern, text):
            return intent
    return "unknown"

# ---------------- Helper functions ----------------
def create_valves_groups(valves_groups):
    groups = re.findall(r'-?\d*\.?\d+', valves_groups)
    res = [float(x) if '.' in x else int(x) for x in groups]
    grps = res[1::2]
    valves = res[::2]
    final_groups = []
    for i in range(len(grps)):
        final_groups = [grps[i]] * valves[i] + final_groups
    return final_groups

def valves_qty():
    return "How many valve groups do you need? (e.g. '3 groups of 2 valves and 1 group of 4 valves')"

# ---------------- Respond ----------------
def respond(intent, user_input):
    global fertikit, ec_ph, weather_station, groups_of_valves

    if intent == "confirm":
        fertikit = input("Do you want to include a Fertikit in the system? (yes/no) ").strip().lower() == "yes"
        ec_ph = input("Do you want to include an EC/PH sensor in the system? (yes/no) ").strip().lower() == "yes"
        weather_station = input("Do you want to include a weather station in the system? (yes/no) ").strip().lower() == "yes"
        return "Great! I've added those to the system. If you want to export the system details to an Excel file, just type 'create excel file'!"

    if intent == "deny":
        groups_of_valves = []
        return "Okay, let's move on."

    if intent == "export_excel":
        system_name = input("Please enter the system name for the Excel file (e.g. singlenet, radionet, Multicable): ")
        parts = generate_parts(system_name, groups_of_valves, fertikit, ec_ph, weather_station)
        filename = export_system_excel(system_name, groups_of_valves, fertikit, ec_ph, weather_station)
        return f"Excel file for {system_name} has been created successfully as {filename}!"

    if intent == "create_valves_groups":
        return create_valves_groups(user_input)

    if intent in ["singlenet", "radionet", "multicable"]:
        return valves_qty()

    if intent == "project_data":
        length = re.findall(r'-?\d*\.?\d+', user_input)
        if not length:
            return "Please provide a numeric field length or area."
        res = [float(x) if '.' in x else int(x) for x in length]
        system = choose_system(res[0])
        return f"For this project, I recommend: {system}"

    if intent == "knowledge_query":
        passage, score = retrieve_relevant_passage(user_input)[0]
        if score < 0.2:
            return "I couldn't find anything relevant."
        return f"Here's what I found: {passage}"

    if intent == "greeting":
        return "Hello! How can I help you today?"

    if intent == "goodbye":
        return "Goodbye! Take care."

    if intent == "help":
        return "I can answer irrigation questions, suggest systems, and create Excel files with parts."

    return "I'm not sure I understand yet, but I am learning."

# ---------------- Chat loop ----------------
def chat():
    print("Chatbot: Hi, I'm your simple chatbot. Type 'bye' to exit.")
    while True:
        user = input("You: ")
        if user.strip().lower() in ["bye", "exit", "quit"]:
            print("Chatbot: Goodbye!")
            break

        intent = predict_intent(user)
        if intent == "Unknown":
            intent = match_intent(user)

        reply = respond(intent, user)
        print("Chatbot:", reply)

if __name__ == "__main__":
    chat()
