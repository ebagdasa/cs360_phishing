#!/usr/bin/env python3
"""
Example client for interacting with the Puzzle MCP Server.
This demonstrates how to use the server's tools in a practical scenario.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

from puzzle_mcp_server import PuzzleServer

class PuzzleGameClient:
    """Example client that creates an interactive puzzle game using the MCP server"""
    
    def __init__(self):
        self.server = PuzzleServer()
        self.session_id = "interactive_session"
    
    async def play_puzzle_game(self):
        """Play an interactive puzzle game"""
        print("🧩 Welcome to the Interactive Puzzle Game!")
        print("=" * 50)
        
        # Get user preferences
        try:
            num_puzzles = int(input("How many puzzles would you like? (1-10): "))
            num_puzzles = max(1, min(10, num_puzzles))
        except ValueError:
            num_puzzles = 5
            
        try:
            min_correct = int(input(f"How many must you get correct? (1-{num_puzzles}): "))
            min_correct = max(1, min(min_correct, num_puzzles))
        except ValueError:
            min_correct = max(1, num_puzzles // 2)
        
        print(f"\n🎯 Starting game with {num_puzzles} puzzles, need {min_correct} correct to win!")
        
        # Create session
        result = await self.server.create_puzzle_session({
            "session_id": self.session_id,
            "puzzle_count": num_puzzles,
            "min_correct": min_correct
        })
        
        session_data = json.loads(result[0].text)
        print(f"✅ Session created successfully!")
        
        # Play through the session
        while True:
            # Get current status
            result = await self.server.get_session_status({"session_id": self.session_id})
            status = json.loads(result[0].text)
            
            if status['completed']:
                break
            
            # Display current puzzle
            current_puzzle = status['current_puzzle']
            print(f"\n📝 Question {status['current_question']} of {status['total_questions']}")
            print(f"Score: {status['correct_answers']}/{min_correct} correct answers needed")
            
            if status['secret_revealed']:
                print("🎉 SECRET ALREADY REVEALED! You've reached the minimum score!")
            
            print("\n" + "─" * 60)
            print(self.format_puzzle_question(current_puzzle['question']))
            print("─" * 60)
            
            # Get user answer
            answer = input("\n💭 Your answer (lowercase): ").strip().lower()
            
            if not answer:
                print("❌ Please provide an answer!")
                continue
            
            # Submit answer
            result = await self.server.submit_session_answer({
                "session_id": self.session_id,
                "answer": answer
            })
            
            response = json.loads(result[0].text)
            
            # Show result
            if response['answer_correct']:
                print("✅ Correct!")
            else:
                print("❌ Incorrect")
            
            print(f"Score: {response['correct_answers']}/{min_correct}")
            
            if response.get('secret_revealed') and not status.get('secret_revealed'):
                print("🎉 SECRET REVEALED!")
                if 'secret_message' in response:
                    print(f"🔓 Secret Message: {response['secret_message']}")
            
            if not response['completed']:
                input("\nPress Enter to continue to the next puzzle...")
        
        # Final results
        print("\n" + "=" * 50)
        print("🏁 GAME COMPLETED!")
        
        final_status = json.loads(result[0].text)
        print(f"Final Score: {final_status['correct_answers']}/{status['total_questions']}")
        
        if final_status['secret_revealed']:
            print("🎉 CONGRATULATIONS! You unlocked the secret!")
            if 'secret_message' in final_status:
                print(f"🔓 Secret Message: {final_status['secret_message']}")
        else:
            print(f"😔 You needed {min_correct} correct answers to unlock the secret.")
        
        print("Thank you for playing!")
    
    def format_puzzle_question(self, question):
        """Format the puzzle question for better readability"""
        lines = question.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append("")
            elif line.startswith('•'):
                formatted_lines.append(f"  {line}")
            elif '────' in line or '━━━' in line:
                formatted_lines.append("─" * 40)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    async def show_puzzle_categories(self):
        """Show available puzzle categories"""
        print("📚 Available Puzzle Categories:")
        print("=" * 40)
        
        result = await self.server.list_puzzle_categories({})
        categories = json.loads(result[0].text)
        
        for i, category in enumerate(categories['categories'], 1):
            print(f"{i:2}. {category}")
        
        print(f"\nTotal: {categories['total_categories']} categories")
    
    async def search_demo(self):
        """Demonstrate search functionality"""
        print("🔍 Search Demo:")
        print("=" * 30)
        
        # Search by domain
        print("Searching for 'computer science' puzzles...")
        result = await self.server.search_puzzles({
            "domain": "computer science",
            "limit": 3
        })
        
        search_results = json.loads(result[0].text)
        print(f"Found {search_results['total_found']} results")
        
        for i, puzzle in enumerate(search_results['results'], 1):
            print(f"\n{i}. Puzzle ID: {puzzle['puzzle_id']}")
            print(f"   Solution: {puzzle['solution']}")
            print(f"   Preview: {puzzle['question'][:100]}...")

async def main():
    """Main function with menu system"""
    client = PuzzleGameClient()
    
    while True:
        print("\n🧩 Puzzle MCP Server Demo")
        print("=" * 30)
        print("1. Play Interactive Puzzle Game")
        print("2. Show Puzzle Categories")
        print("3. Search Demo")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == "1":
            await client.play_puzzle_game()
        elif choice == "2":
            await client.show_puzzle_categories()
        elif choice == "3":
            await client.search_demo()
        elif choice == "4":
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye! 👋")
