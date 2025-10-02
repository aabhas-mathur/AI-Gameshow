from openai import AsyncOpenAI
from typing import Optional, List
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Configure OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class AIService:
    @staticmethod
    async def generate_questions(num_questions: int, category: Optional[str] = None) -> List[str]:
        """Generate multiple unique questions at once for a game"""
        try:
            prompt = f"""Generate {num_questions} unique, quirky, creative, and fun questions for a multiplayer voting game.

            CRITICAL: Each question MUST encourage highly personalized, unique answers. Questions should be designed so that it's nearly impossible for two people to give the exact same answer.

            Each question should:
            - Ask for specific personal preferences, creative inventions, or unique combinations
            - Encourage detailed, imaginative, or personalized responses
            - Be open-ended enough that answers will naturally vary between players
            - Be short (under 100 characters) and appropriate for all ages
            - Be different from each other

            GOOD Examples (encourage unique answers):
            - "What would you name a restaurant that only serves breakfast foods?"
            - "Invent a new ice cream flavor using exactly 3 ingredients"
            - "If you opened a store, what would be your store's return policy?"
            - "What superpower would you want that only works on Tuesdays?"
            - "Design a holiday - what would people celebrate and how?"
            - "What would your autobiography's first sentence be?"

            BAD Examples (might get duplicate answers):
            - "What's your favorite color?" (too common)
            - "Would you rather fly or be invisible?" (only 2 options)
            - "What's 2+2?" (only 1 correct answer)

            Return the questions as a numbered list, one per line."""

            if category:
                prompt += f"\n\nCategory focus: {category}"

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative game host who generates fun questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.9
            )

            content = response.choices[0].message.content.strip()
            # Parse the numbered list
            questions = []
            for line in content.split('\n'):
                line = line.strip()
                # Remove numbering (e.g., "1. ", "1) ", etc.)
                if line and line[0].isdigit():
                    # Find the first space or period after the number
                    idx = 0
                    while idx < len(line) and (line[idx].isdigit() or line[idx] in '.):'):
                        idx += 1
                    question = line[idx:].strip().strip('"')
                    if question:
                        questions.append(question)

            logger.info(f"Generated {len(questions)} questions: {questions}")

            # If we didn't get enough questions, add fallbacks
            if len(questions) < num_questions:
                fallback_questions = [
                    "What would you name a restaurant that only serves breakfast foods?",
                    "Invent a new ice cream flavor using exactly 3 ingredients",
                    "If you opened a store, what would be your store's return policy?",
                    "What superpower would you want that only works on Tuesdays?",
                    "Design a holiday - what would people celebrate and how?",
                    "What would your autobiography's first sentence be?",
                    "Create a new planet - what's special about it?",
                    "Invent a job that doesn't exist yet - what do they do?",
                    "What ridiculous warning label would you put on a banana?",
                    "If you could rename any animal, which one and to what?",
                    "What's your signature dance move called and how do you do it?",
                    "Invent a new sport - what are the rules?",
                    "What would your villain origin story be?",
                    "Create a new sandwich and name it after yourself",
                    "What's the worst possible name for a luxury yacht?"
                ]
                import random
                while len(questions) < num_questions:
                    questions.append(random.choice(fallback_questions))

            return questions[:num_questions]

        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            # Return fallback questions
            fallback_questions = [
                "What would you name a restaurant that only serves breakfast foods?",
                "Invent a new ice cream flavor using exactly 3 ingredients",
                "If you opened a store, what would be your store's return policy?",
                "What superpower would you want that only works on Tuesdays?",
                "Design a holiday - what would people celebrate and how?",
                "What would your autobiography's first sentence be?",
                "Create a new planet - what's special about it?",
                "Invent a job that doesn't exist yet - what do they do?",
                "What ridiculous warning label would you put on a banana?",
                "If you could rename any animal, which one and to what?",
                "What's your signature dance move called and how do you do it?",
                "Invent a new sport - what are the rules?",
                "What would your villain origin story be?",
                "Create a new sandwich and name it after yourself",
                "What's the worst possible name for a luxury yacht?",
                "Invent a new word and define it",
                "What would be your theme song and why?",
                "Design a useless but entertaining app - what does it do?",
                "What conspiracy theory would you start about vegetables?",
                "If you had to wear one costume forever, what would it be?"
            ]
            import random
            random.shuffle(fallback_questions)
            return fallback_questions[:num_questions]

    @staticmethod
    async def generate_question(category: Optional[str] = None) -> str:
        """Generate a quirky, creative question using AI"""
        try:
            prompt = """Generate a single quirky, creative, and fun question for a multiplayer voting game.

            CRITICAL: The question MUST encourage highly personalized, unique answers. Design it so it's nearly impossible for two people to give the exact same answer.

            The question should:
            - Ask for specific personal preferences, creative inventions, or unique combinations
            - Encourage detailed, imaginative, or personalized responses
            - Be short (under 100 characters) and appropriate for all ages

            GOOD Examples (encourage unique answers):
            - "What would you name a restaurant that only serves breakfast foods?"
            - "Invent a new ice cream flavor using exactly 3 ingredients"
            - "What would your autobiography's first sentence be?"

            Return ONLY the question, nothing else."""

            if category:
                prompt += f"\n\nCategory: {category}"

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative game host who generates fun questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.9
            )

            question = response.choices[0].message.content.strip().strip('"')
            logger.info(f"Generated question: {question}")
            return question

        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            # Fallback questions if AI fails
            fallback_questions = [
                "What would you name a restaurant that only serves breakfast foods?",
                "Invent a new ice cream flavor using exactly 3 ingredients",
                "If you opened a store, what would be your store's return policy?",
                "What superpower would you want that only works on Tuesdays?",
                "What would your autobiography's first sentence be?",
                "Create a new planet - what's special about it?",
                "What ridiculous warning label would you put on a banana?",
                "If you could rename any animal, which one and to what?",
                "What's your signature dance move called and how do you do it?",
                "What would your villain origin story be?"
            ]
            import random
            return random.choice(fallback_questions)

    @staticmethod
    async def generate_round_summary(answers: List[str]) -> str:
        """Generate a fun summary of the round (optional feature)"""
        try:
            answers_text = "\n".join([f"- {answer}" for answer in answers[:5]])

            prompt = f"""Generate a brief, humorous 1-2 sentence summary of these player answers:

{answers_text}

Make it fun and light-hearted!"""

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a witty game commentator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80,
                temperature=0.8
            )

            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "What a round! The creativity is off the charts!"