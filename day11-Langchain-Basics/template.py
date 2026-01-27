"""LLM Service module for text processing tasks."""

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============ Public Exports ============
__all__ = [
    'TEMPLATE',
    'INSTRUCTIONS',
    'chain',
    'invoke_chain',
    'summarize',
    'translate',
    'qa',
    'classify',
]

# ============ Configuration ============
TEMPLATE = '''
System:
{instruction}

H: {prompt}
'''

INSTRUCTIONS = {
    'summarize': 'The chatbot should summarize whatever the user sends',
    'translate': 'The chatbot should translate to french whatever the user sends',
    'qa': 'The chatbot should answer every question whatever the user sends',
    'classify': 'The chatbot should classify into categories whatever the user sends',
}

# ============ Setup ============
_prompt_template = PromptTemplate.from_template(template=TEMPLATE)
_llm = ChatOpenAI(model="gpt-3.5-turbo")
chain = _prompt_template | _llm


# ============ Core Function ============
def invoke_chain(instruction: str, prompt: str) -> str:
    """Base function to invoke the chain with given instruction and prompt."""
    response = chain.invoke({
        'instruction': instruction,
        'prompt': prompt
    })
    return response.content


# ============ Task Functions ============
def summarize(prompt: str) -> str:
    """Summarize the given text."""
    return invoke_chain(INSTRUCTIONS['summarize'], prompt)


def translate(prompt: str) -> str:
    """Translate the given text to French."""
    return invoke_chain(INSTRUCTIONS['translate'], prompt)


def qa(prompt: str) -> str:
    """Answer questions based on the given prompt."""
    return invoke_chain(INSTRUCTIONS['qa'], prompt)


def classify(prompt: str) -> str:
    """Classify the given text into categories."""
    return invoke_chain(INSTRUCTIONS['classify'], prompt)


# ============ Main Execution ============
if __name__ == "__main__":
    user_prompt = input('What do you want me to summarize? \n')
    print(f"\n{summarize(user_prompt)}")