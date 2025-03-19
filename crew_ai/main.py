from agents import InterviewAgents
from tasks import InterviewingTasks
from crewai import Crew
from dotenv import load_dotenv
load_dotenv()

tasks = InterviewingTasks()
agents = InterviewAgents()

Question='What is the importance of responding to risks and threats according to organizational and legal protocols?'
interviewer_answer='Responding to risks and threats in line with organizational and legal protocols is essential to ensure the safety of individuals and property, maintain legal compliance, and protect the reputation and liability of the organization.'
interviewee_answer = "To guarantee the protection of individuals and property"
# interviewee_answer="To risk the safety of individuals and property, and neglect legal compliance."
# interviewee_answer= "to ensure the safety of individuals and property, maintain legal compliance"
#interviewee_answer="i cannot say this"


feedback_agent = agents.Feedback(interviewee_answer, interviewer_answer)
score_agent = agents.Score(interviewee_answer, interviewer_answer)
Answer_Feedback = tasks.GiveFeedback(
    feedback_agent, interviewee_answer, interviewer_answer)
Score_Answer = tasks.Scorer(
    score_agent, interviewee_answer, interviewer_answer)

crew1 = Crew(
    agents=[
        feedback_agent,
        score_agent
    ],
    tasks=[
        Answer_Feedback,
        Score_Answer
    ],
    verbose=False
)

crew_output = crew1.kickoff()