# -*- coding: utf-8 -*-
"""
Created on Sat Feb 28 06:54:08 2026

@author: HOMELC009452
"""


##################################################################################################
# 01 - Bring in .env information
##################################################################################################

import os
from dotenv import load_dotenv
load_dotenv()


##################################################################################################
# 02 - Create the connection string for the postgres database
##################################################################################################

POSTGRES_URI = (f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
                f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DBNAME')}?sslmode=require")


##################################################################################################
# 03 - Create the database engine
##################################################################################################

import sqlalchemy as sa

# create the database engine
engine = sa.create_engine(POSTGRES_URI,
                          pool_pre_ping=True,
                          connect_args={"options": "-c statement_timeout=15000"} # 15 second timeout
                          ) 

# check the connection
with engine.connect() as conn:
    conn.exec_driver_sql("select 1")
    

##################################################################################################
# 04 - Setup the database connection
##################################################################################################

from langchain_community.utilities import SQLDatabase

db = SQLDatabase(engine=engine,
                 schema="grocery_db",
                 include_tables=["customer_details", "transactions"], # only 2 tables access is allowed
                 sample_rows_in_table_info=5) #allows langchain to fetch 5rows from both the tables, to get an idea of the data

print("Usable tables:", db.get_usable_table_names())



##################################################################################################
# 05 - Create our SQL AI Agent
##################################################################################################

from langchain_openai import ChatOpenAI

sql_agent = ChatOpenAI(model="gpt-4.1", 
                       temperature=0)


##################################################################################################
# 06 - Build the SQL Toolkit and tools
##################################################################################################

from langchain_community.agent_toolkits import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=db, llm=sql_agent) # this lets agents to talk to SQL database rather than just write queries
tools = toolkit.get_tools()


##################################################################################################
# 07 - Bring In System Prompt
##################################################################################################

# bring in the system instructions
with open("sql-agent-system-prompt.txt", "r", encoding="utf-8") as f:
    system_text = f.read()
    
    
##################################################################################################
# 08 - Create the Agent
##################################################################################################

from langchain.agents import create_agent

agent = create_agent(model=sql_agent,
                     tools=tools,
                     system_prompt=system_text)


##################################################################################################
# 09 - Streamlit frontend - import the libraries
##################################################################################################

import streamlit as st
import pandas as pd


##################################################################################################
# 10 - Add title and instructions
##################################################################################################

st.title("Population Stats")
st.subheader("What do you want to check? ")

user_input = st.text_input("Enter your query",value = "On average which gender lives furthest from store?")


##################################################################################################
# 11 - Run test queries through the agent and extract the response
##################################################################################################

from langchain_core.messages import HumanMessage

#user_query = "On average which gender lives furthest from store?"

if st.button("Submit"):
    user_query = user_input
    result = agent.invoke({"messages": [HumanMessage(content=user_query)]})
    print(result["messages"][-1].content)


##################################################################################################
# 12 - Print result on streamlit
##################################################################################################

    st.subheader(result["messages"][-1].content)






    


