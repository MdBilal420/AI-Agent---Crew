# Warning control
# import warnings
# warnings.filterwarnings('ignore')

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from crewai import Agent, Task, Crew

import os
import streamlit as st
# from utils import get_openai_api_key, pretty_print_result


openai_api_key = os.environ["OPENAI_API_KEY"]
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'
from crewai_tools import DirectoryReadTool, \
                         FileReadTool, \
                         SerperDevTool



sales_rep_agent = Agent(
    role="Sales Representative",
    goal="Identify high-value leads that match "
         "our ideal customer profile",
    backstory=(
        "As a part of the dynamic sales team at Wilya, "
        "your mission is to scour "
        "the digital landscape for potential leads. "
        "Armed with cutting-edge tools "
        "and a strategic mindset, you analyze data, "
        "trends, and interactions to "
        "unearth opportunities that others might overlook. "
        "Your work is crucial in paving the way "
        "for meaningful engagements and driving the company's growth."
    ),
    allow_delegation=False,
    verbose=True
)

lead_sales_rep_agent = Agent(
    role="Lead Sales Representative",
    goal="Nurture leads with personalized, compelling communications",
    backstory=(
        "Within the vibrant ecosystem of Wilya's sales department, "
        "you stand out as the bridge between potential clients "
        "and the solutions they need."
        "some of the solutions that we provide are by digitizing your skills matrix, flexible workforce and flex shifts"
        # "By digitizing their skill matrix and operationalizing it they went from hours on the phone to find coverage to a few clicks on their phone and coverage within the hour."
        # "Wilya has partnered with top manufacturers to solve the flexibility challenge while maintaining ownership of the talent pool, onboarding and safety priorities."
        "By creating engaging, personalized messages, "
        "you not only inform leads about our offerings "
        "but also make them feel seen and heard."
        "Your role is pivotal in converting interest "
        "into action, guiding leads through the journey "
        "from curiosity to commitment."
    ),
    allow_delegation=False,
    verbose=True
)



directory_read_tool = DirectoryReadTool(directory='./instructions')
file_read_tool = FileReadTool()
search_tool = SerperDevTool()

from crewai_tools import BaseTool

class SentimentAnalysisTool(BaseTool):
    name: str ="Sentiment Analysis Tool"
    description: str = ("Analyzes the sentiment of text "
         "to ensure positive and engaging communication.")
    
    def _run(self, text: str) -> str:
        # Your custom code tool goes here
        return "positive"
    
sentiment_analysis_tool = SentimentAnalysisTool()

lead_profiling_task = Task(
    description=(
        "Conduct an in-depth analysis of {lead_name}, "
        "a company in the {industry} sector "
        "that recently showed interest in our solutions. "
        "Utilize all available data sources "
        "to compile a detailed profile, "
        "focusing on key decision-makers, recent business "
        "developments, and potential needs "
        "that align with our offerings. "
        "This task is crucial for tailoring "
        "our engagement strategy effectively.\n"
        "Don't make assumptions and "
        "only use information you absolutely sure about."
    ),
    expected_output=(
        "A comprehensive report on {lead_name}, "
        "including company background, "
        "key personnel, recent milestones, and identified needs. "
        "Highlight potential areas where "
        "our solutions can provide value, "
        "and suggest personalized engagement strategies."
    ),
    tools=[directory_read_tool, file_read_tool, search_tool],
    agent=sales_rep_agent,
)

personalized_outreach_task = Task(
    description=(
        "Using the insights gathered from "
        "the lead profiling report on {lead_name}, "
        "craft a personalized outreach campaign "
        "aimed at {key_decision_maker}, "
        "the {position} of {lead_name}. "
        "The campaign should address their recent {milestone} "
        "and how our solutions can support their goals. "
        "Your communication must resonate "
        "with {lead_name}'s company culture and values, "
        "demonstrating a deep understanding of "
        "their business and needs.\n"
        "Don't make assumptions and only "
        "use information you absolutely sure about."
    ),
    expected_output=(
        "A series of personalized email drafts "
        "tailored to {lead_name}, "
        "specifically targeting {key_decision_maker}."
        "Each draft should include "
        "a compelling narrative that connects our solutions "
        "with their recent achievements and future goals. "
        "Ensure the tone is engaging, professional, "
        "and aligned with {lead_name}'s corporate identity."
    ),
    tools=[sentiment_analysis_tool, search_tool],
    agent=lead_sales_rep_agent,
)

crew = Crew(
    agents=[sales_rep_agent, 
            lead_sales_rep_agent],
    
    tasks=[lead_profiling_task, 
           personalized_outreach_task],
	
    verbose=2,
	memory=True
)

st.title("Customer Outreach Form")

col1, col2 = st.columns(2)
with col1:
    lead_name = st.text_input("Lead Name")

with col2:
    industry = st.text_input("Industry")

col3, col4 = st.columns(2)
with col3:
    key_decision_maker = st.text_input("Key Decision Maker")

with col4:
    position = st.text_input("Position")

milestone = st.text_input("Milestone")


result = []

with st.form(
    "myform",
    clear_on_submit=True
):
    inputs = {
    "lead_name": {lead_name},
    "industry": {industry},
    "key_decision_maker": {key_decision_maker},
    "position": {position},
    "milestone": {milestone}
    }

    submitted = st.form_submit_button(
        "Submit",
        disabled=not (lead_name and industry and key_decision_maker and position and milestone)
    )
    
    if submitted:
        with st.spinner("Wait, please. I am working on it..."):
            response = crew.kickoff(inputs=inputs)
            result.append(response)

if(len(result)):
    st.markdown(response)


