from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage

class AgentState(TypedDict):
    agent: str
    initialMessage: str
    responseToUser: str
    lnode: str
    category: str

class Category(BaseModel):
    category: str


VALID_CATEGORIES = ["policy", "commission", "contest", "ticket", "clarify"]


class salesCompAgent():
    def __init__(self, api_key):
        self.model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=api_key)

        builder = StateGraph(AgentState)
        builder.add_node("classifier", self.initial_classifier)

        builder.add_node("policy", self.policy_agent)
        builder.add_node("commission", self.commission_agent)
        builder.add_node("contest", self.contest_agent)
        builder.add_node("ticket", self.ticket_agent)
        builder.add_node("clarify", self.clarify_agent)

        builder.set_entry_point("classifier")
        builder.add_conditional_edges("classifier", self.main_router, 
                                      {
                                          "policy": "policy", 
                                          "commission": "commission",
                                          "contest": "contest",
                                          "ticket": "ticket",
                                          "clarify": "clarify",
                                      })

        builder.add_edge("policy", END)
        builder.add_edge("commission", END)
        builder.add_edge("contest", END)
        builder.add_edge("ticket", END)
        builder.add_edge("clarify", END)

        memory = SqliteSaver(conn=sqlite3.connect(":memory:", check_same_thread=False))
        self.graph = builder.compile(checkpointer = memory)
        #self.graph.get_graph().draw_png('graph.png')

    def initial_classifier(self, state: AgentState):
        print("initial_classifier")
        classifier_prompt = f"""
        You are an expert at customer service in Sales Operations. Please classify the customer
        request as follows:
        1) If the request is a question about sales policies, category is 'policy'
        2) If the request is a quetsion about user's commissions, category is 'commission'
        3) If the request is a question about sales contests, category is 'contest' 
        4) If the request is a question about tickets, category is 'ticket'
        5) otherwise ask the user to clarify the request, category is 'clarify'
        """

        llm_response = self.model.with_structured_output(Category).invoke([
            SystemMessage(content=classifier_prompt), 
            HumanMessage(content=state['initialMessage']),
        ])
        category = llm_response.category
        print(f"category is {category}")


        self.responseToUser = "great job"
        return {
            "lnode": "initial_router", 
            "responseToUser": "success",
            "category": category
        }

    def policy_agent(self, state:AgentState):
        print("policy agent")

    def commission_agent(self, state:AgentState):
        print("commission agent")

    def contest_agent(self, state:AgentState):
        print("contest agent")

    def ticket_agent(self, state:AgentState):
        print("ticket agent")

    def clarify_agent(self, state:AgentState):
        print("clarify agent")

    def main_router(self, state:AgentState):
        my_category = state['category']
        if my_category in VALID_CATEGORIES:
            return my_category
        else:
            print(f"unknown category: {my_category}")
            return END