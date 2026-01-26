from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

def JSON_Output_Parser():

    class Person(BaseModel):
        name: str = Field(description="The person's full name")
        age: int = Field(description= "Age in years")
        city: str = Field(description= "City they live in")

    parser = JsonOutputParser(pydantic_object=Person)

    model = ChatOpenAI()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract person info. {format_instructions}"),
        ("human", "{input}")
    ])

    chain = prompt | model | parser

    result = chain.invoke({
        "input": "John is 25 and lives in NYC",
        "format_instructions": parser.get_format_instructions()
    })

    print(result)

def Specfield():
    """ 
    Extracting Speciific fields
    """
    prompt = ChatPromptTemplate(
        [
                ("system", "You are a movie reviewer"),
                ("human", "{input}")
        ])

    model = ChatOpenAI(model="gpt-5-nano")

    class MovieReview(BaseModel):
        sentiment: str = Field(description= "positive, negative or neutral")
        score: int = Field(description= "Rating from 1-10")


    structured_model = model.with_structured_output(MovieReview, include_raw= True)

    chain = prompt | structured_model
    safe_chain = chain.with_retry(stop_after_attempt=3)

    user_input = input("What movie do you wanna review?     ")
    response = safe_chain.invoke({"input": user_input})


    if response["parsed"] is not None:
        print(f"Success! Sentiment:{response['parsed'].sentiment}")
        print(f"Success! Score: {response['parsed'].score}")
    else:
        print("Parse Failed!")
        print(f"Raw Output was: {response['raw']}")

if __name__ == "__main__":
    Specfield()