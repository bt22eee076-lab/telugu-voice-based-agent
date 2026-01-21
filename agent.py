import json

def scheme_retrieval_tool(scheme_name):
    """
    Tool: Retrieves scheme details from knowledge base.
    """
    with open("schemes.json", "r", encoding="utf-8") as f:
        schemes = json.load(f)

    return schemes.get(scheme_name)

# Agent memory (will persist during runtime)
agent_memory = {
    "language": "te",
    "user_goal": None,
    "collected_info": {},
    "last_user_input": None,
    "expected_input": None
}


def eligibility_engine(memory):
    """
    Tool: Determines eligibility based on collected info.
    """
    age = memory["collected_info"].get("age")
    income = memory["collected_info"].get("income")
    state = memory["collected_info"].get("state")

    eligible_schemes = []

    # Example rules (mock but realistic)
    if age is not None and income is not None:
        if age >= 18 and income < 200000:
            eligible_schemes.append("ఆర్థిక సహాయం పథకం")

        if age < 25:
            eligible_schemes.append("యువ అభివృద్ధి పథకం")

    if state == "తెలంగాణ":
        eligible_schemes.append("తెలంగాణ రాష్ట్ర సంక్షేమ పథకం")

    return eligible_schemes


def planner(user_text, memory):
    if memory["user_goal"] is None:
        memory["user_goal"] = "FIND_SCHEME"
        memory["expected_input"] = "AGE"
        return "ASK_AGE"

    if "age" not in memory["collected_info"]:
        memory["expected_input"] = "AGE"
        return "ASK_AGE"

    if "income" not in memory["collected_info"]:
        memory["expected_input"] = "INCOME"
        return "ASK_INCOME"

    if "state" not in memory["collected_info"]:
        memory["expected_input"] = "STATE"
        return "ASK_STATE"

    memory["expected_input"] = None
    if memory.get("expected_input") == "APPLY_CONFIRM":
       return "HANDLE_APPLICATION"

    return "CHECK_ELIGIBILITY"



def executor(action, memory):
    if action == "ASK_AGE":
        return "మీ వయస్సు ఎంత?"

    if action == "ASK_INCOME":
        return "మీ వార్షిక ఆదాయం ఎంత?"

    if action == "ASK_STATE":
        return "మీరు ఏ రాష్ట్రంలో ఉంటున్నారు?"

    if action == "CHECK_ELIGIBILITY":
        schemes = eligibility_engine(memory)

        if not schemes:
            return "క్షమించండి, ప్రస్తుతం మీకు సరిపోయే పథకం కనిపించలేదు."

        response = "మీకు ఈ పథకాలు వర్తించవచ్చు:\n\n"
        
        if action == "HANDLE_APPLICATION":
            if "అవును" in memory["last_user_input"]:
                return "దయచేసి దగ్గరలోని ప్రభుత్వ కార్యాలయాన్ని సందర్శించండి లేదా అధికారిక వెబ్‌సైట్‌లో దరఖాస్తు చేయండి."
            else:
                return "సరే. మరేదైనా సహాయం కావాలంటే చెప్పండి."


        for s in schemes:
            details = scheme_retrieval_tool(s)

            if details:
                response += f"🔹 {s}\n"
                response += f"వివరణ: {details['description']}\n"
                response += f"లాభాలు: {details['benefits']}\n"
                response += f"అవసరమైన పత్రాలు: {details['documents']}\n\n"
            else:
                response += f"🔹 {s}\nవివరాలు లభ్యం కావు.\n\n"

        response += "మీరు ఈ పథకానికి దరఖాస్తు చేయాలనుకుంటున్నారా? అవును లేదా కాదు అని చెప్పండి."
        memory["expected_input"] = "APPLY_CONFIRM"
        return response


    return "దయచేసి మళ్లీ చెప్పండి."


def evaluator(response_text):
    """
    Check response quality before speaking.
    """
    if not response_text or len(response_text.strip()) == 0:
        return "క్షమించండి, దయచేసి మళ్లీ చెప్పండి."

    return response_text

def extract_information(text, memory):
    expected = memory.get("expected_input")

    # AGE
    if expected == "AGE":
        numbers = [int(s) for s in text.split() if s.isdigit()]
        if numbers:
            new_age = numbers[0]
            conflict, old_age = check_contradiction("age", new_age, memory)

            if conflict:
                memory["conflict"] = f"మీరు ముందు {old_age} చెప్పారు, ఇప్పుడు {new_age} చెప్పారు. సరైన వయస్సు చెప్పండి."
            else:
                memory["collected_info"]["age"] = new_age
                memory["conflict"] = None


    # INCOME
    if expected == "INCOME":
        numbers = [int(s) for s in text.split() if s.isdigit()]
        if numbers:
            new_income = numbers[0]
            conflict, old_income = check_contradiction("INCOME", new_income, memory)

            if conflict:
                memory["conflict"] = f"మీరు ముందు {old_income} చెప్పారు, ఇప్పుడు {new_income} చెప్పారు. సరైన వయస్సు చెప్పండి."
            else:
                memory["collected_info"]["income"] = new_income
                memory["conflict"] = None


    # STATE
    if expected == "STATE":
        numbers = [int(s) for s in text.split() if s.isdigit()]
        if numbers:
            new_state = numbers[0]
            conflict, old_state = check_contradiction("state", new_age, memory)

            if conflict:
                memory["conflict"] = f"మీరు ముందు {old_state} చెప్పారు, ఇప్పుడు {new_state} చెప్పారు. సరైన వయస్సు చెప్పండి."
            else:
                memory["collected_info"]["state"] = new_state
                memory["conflict"] = None



def check_contradiction(key, new_value, memory):
    old_value = memory["collected_info"].get(key)

    if old_value is not None and old_value != new_value:
        return True, old_value

    return False, None


import speech_recognition as sr
from gtts import gTTS
import os

def speak(text):
    tts = gTTS(text=text, lang="te")
    filename = "agent_response.mp3"
    tts.save(filename)
    os.startfile(filename)

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ మాట్లాడండి...")
        r.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = r.listen(
                source,
                timeout=5,            # wait max 5 seconds to start
                phrase_time_limit=5   # max speaking time
            )
        except sr.WaitTimeoutError:
            return None

    try:
        return r.recognize_google(audio, language="te-IN") # type: ignore
    except sr.UnknownValueError:
        return "UNRECOGNIZED"
    except sr.RequestError:
        return "SERVICE_ERROR"



while True:

    user_input = listen()
    if agent_memory.get("conflict"):
     speak(agent_memory["conflict"])
     continue


    if user_input is None:
        speak("మీరు మాట్లాడలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.")
        continue

    if user_input == "UNRECOGNIZED":
        speak("మీ మాటలు స్పష్టంగా లేవు. మళ్లీ చెప్పండి.")
        continue

    if user_input == "SERVICE_ERROR":
        speak("సేవలో సమస్య ఉంది. కొద్దిసేపటి తర్వాత ప్రయత్నించండి.")
        continue


    agent_memory["last_user_input"] = user_input
    extract_information(user_input, agent_memory)
    print("User:", user_input)

    action = planner(user_input, agent_memory)
    response = executor(action, agent_memory)
    response = evaluator(response)

    speak(response)
