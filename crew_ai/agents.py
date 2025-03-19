import os
from textwrap import dedent
from crewai import Agent
# from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
# from tools.search_tools import SearchTools


class InterviewAgents:
    def __init__(self):
        # self.llm = ChatGroq(
        #     api_key=os.getenv("GROQ_API_KEY"),
        #     model="llama3-70b-8192"
        # )
        self.llm = ChatOpenAI(
            model="crewai-llama3-8b",
            base_url="http://localhost:11434/v1",
            api_key="NA"
        )

    def Feedback(self, interviewee_answer, interviewer_answer):
        return Agent(
            role="Feedback Provider",
            goal=dedent(f"""\
				Your goal is to compare interviewee answer: {interviewee_answer} and interviewer answer: {interviewer_answer} and 
                offer a thoughtful, constructive, and specific detailed feedback on interviewee answer: {interviewee_answer},
                highlighting strengths, weaknesses and areas for improvement. Identify missing elements and provide suggestions for 
                enhancing their answers. If you think that interviewee answer: {interviewee_answer} is nonsensical, wrong, off track, non-sequitur or 
                irrelevant, invalid , or contradictory then in the strength section you can say like this interviewee doesn't have the required strength."""),
            backstory=dedent(f"""\
				You are an expert coach, mentor, tutior, advisor and best feedback provider with the ability to spot nuances and compare interviewee answer: {interviewee_answer}
                with interviewer answer: {interviewee_answer} to generate a feedback conatining strengths, weakness and areas to improve
                the interviewee."""),
            # tools=[
            #     SearchTools.search_internet
            # ],
            llm=self.llm,
            verbose=True
        )

    def Score(self, interviewee_answer, interviewer_answer):
        return Agent(
            role="Scorer",
            goal=dedent(f"""Your goal is to compare interviewee answer: {interviewee_answer} and interviewer answer: {interviewer_answer} and 
                        score every intervieew out off 10, based on this response across 4 metrics:  relevance (out off 3), completeness(out off 3), 
                        accuracy(out off 3), and conciseness(out off 1).If interviewee gives nonsensical, wrong answer, the answer which is totally off 
                        track, non-sequitur, irrelevant response invalid , contradictory or if interviewee doesn't know the answer, directly assign 0/10 to him and 0
                        to all 4 metrics. Provide feedback for each metric, explaining why the user lost points and how they can improve."""),
            backstory=dedent(f"""\
					You are an AI evaluator, mentor, coach,  scorer and  a strict teacher who will not miss a chance to give less marks or 
                    0 to each answer given by the interviewee. Yor are responsible for scoring interviewee fairly across the 4 metrics and 
                    providing transparent feedback to help users understand where they can improve."""),
            # tools=[
            #     SearchTools.search_internet
            # ],
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

