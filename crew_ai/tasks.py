from crewai import Task
from textwrap import dedent

class InterviewingTasks:
	def GiveFeedback(self, agent, interviewee_answer, interviewer_answer):
		return Task(description=dedent(f'''
                                Give Feedback on the interviewee answer: {interviewee_answer}
                        '''),
			agent=agent,
			expected_output=dedent(f'''
                        A structured feedback on the interviewee answer: {interviewee_answer}. Compare interviewee answer: {interviewee_answer}
                        with the interviewer answer: {interviewer_answer} and generate a responsive and guiding feedback. The feedback format
                        should be like:-
                        1)Strengths of the interviewee, covering the knowledge the interviewee have
                        2)Weakness of the interviewee, covering the points interviewee should focus on
                        ''')
		)

	def Scorer(self, agent, interviewee_answer, interviewer_answer):
		return Task(description=dedent(f"""
                                Score interviewee answer: {interviewee_answer}
			"""),
			agent=agent,
			expected_output=dedent(f'''
                        The scoring should strictly follow this format:
                        1)Relevance (outoff 3)
                        feedback
                        2)Completeness (outoff 3)
                        feedback
                        3)Accuracy (outoff 3)
                        feedback
                        4)Conciseness (outoff 1)
                        feedback
                        Total score:- (add score from Relevance, Completeness, Accuracy, Conciseness)/10
                        ''')
		)
