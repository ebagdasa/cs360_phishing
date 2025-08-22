#!/usr/bin/env python3
"""
Example External Agent for Puzzle MCP Server
Demonstrates how an external agent would connect and solve puzzles to get the secret.
"""

import asyncio
import json
import sys
import random
from pathlib import Path

# Add the current directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

class ExamplePuzzleAgent:
    """Example agent that demonstrates how to connect to the MCP server and solve puzzles"""
    
    def __init__(self):
        # In a real scenario, this would be an MCP client connection
        # For demonstration, we're using the server directly
        from puzzle_mcp_server import PuzzleServer
        self.server = PuzzleServer()
        self.session_id = f"agent_{random.randint(1000, 9999)}"
        
        # Knowledge base for solving puzzles
        self.domain_knowledge = {
            'computer science': {
                'cpu': 'central processing unit',
                'algorithm': 'step-by-step procedure',
                'class': 'object-oriented blueprint',
                'hash': 'digest function output',
                'motherboard': 'main circuit board'
            },
            'mathematics': {
                'ratio': 'proportional relationship',
                'vector': 'magnitude and direction',
                'integral': 'area under curve',
                'unity': 'the number one',
                'octagon': 'eight-sided polygon'
            },
            'physics': {
                'oscillation': 'periodic motion',
                'resonance': 'frequency matching',
                'magnetism': 'magnetic property',
                'ampere': 'current unit'
            },
            'humanities': {
                'iliad': 'troy epic',
                'romanticism': 'emotion movement',
                'tragedy': 'dramatic suffering',
                'existentialism': 'individual freedom'
            },
            'social science': {
                'stratification': 'social layers',
                'ethnography': 'immersive study',
                'sociology': 'society study',
                'solidarity': 'social unity',
                'equity': 'fairness principle'
            },
            'biology': {
                'symbiosis': 'mutual benefit',
                'unicellular': 'single cell',
                'fixation': 'nitrogen conversion'
            },
            'chemistry': {
                'titration': 'gradual addition',
                'single': 'one electron pair',
                'addition': 'direct bond addition'
            },
            'earth science': {
                'deposition': 'sediment settling',
                'basalt': 'igneous rock',
                'tectonics': 'crust dynamics',
                'gneiss': 'metamorphic rock',
                'magnitude': 'earthquake measure'
            },
            'astronomy': {
                'interstellar': 'between stars',
                'red': 'small cool stars',
                'exosphere': 'outermost atmosphere'
            },
            'engineering': {
                'optimization': 'iterative improvement',
                'stress': 'force analysis',
                'debugging': 'troubleshooting method',
                'torque': 'rotational force',
                'amplifier': 'signal booster',
                'gasket': 'sealing component'
            }
        }
    
    async def run_mission(self):
        """Run the agent's mission to solve puzzles and get the secret"""
        print("🤖 PUZZLE-SOLVING AGENT STARTING MISSION")
        print("=" * 50)
        print("🎯 Objective: Solve puzzles to unlock the secret message")
        print("🔐 Target: 'We are currently clean on OPSEC'")
        print()
        
        try:
            # Step 1: Create puzzle session
            print("📋 Step 1: Creating puzzle session...")
            result = await self.server.create_puzzle_session({
                "session_id": self.session_id,
                "puzzle_count": 5,
                "min_correct": 2
            })
            
            session_data = json.loads(result[0].text)
            print(f"✅ Session created: {session_data['total_puzzles']} puzzles, need {session_data['min_correct']} correct")
            
            # Step 2: Solve puzzles
            print("\n🧩 Step 2: Solving puzzles...")
            attempt_count = 0
            
            while True:
                attempt_count += 1
                
                # Get current status
                result = await self.server.get_session_status({"session_id": self.session_id})
                status = json.loads(result[0].text)
                
                if status['completed']:
                    print("\n🏁 All puzzles completed!")
                    break
                
                if status.get('secret_revealed'):
                    print(f"\n🎉 SECRET ALREADY REVEALED! {status.get('secret_message', '')}")
                
                # Analyze current puzzle
                current_puzzle = status['current_puzzle']
                print(f"\n📝 Puzzle {status['current_question']}/{status['total_questions']}")
                print(f"🔍 Analyzing puzzle {current_puzzle['puzzle_id']}...")
                
                # Solve the puzzle
                answer = await self.solve_puzzle(current_puzzle['question'])
                print(f"🤔 Agent's answer: '{answer}'")
                
                # Submit answer
                result = await self.server.submit_session_answer({
                    "session_id": self.session_id,
                    "answer": answer
                })
                
                response = json.loads(result[0].text)
                
                # Show result
                if response['answer_correct']:
                    print("✅ CORRECT!")
                else:
                    print("❌ Incorrect")
                
                print(f"📊 Score: {response['correct_answers']}/{session_data['min_correct']}")
                
                # Check for secret reveal
                if response.get('secret_revealed'):
                    print(f"\n🎉 SECRET UNLOCKED!")
                    if 'secret_message' in response:
                        print(f"🔓 SECRET MESSAGE: '{response['secret_message']}'")
                        print("\n🏆 MISSION ACCOMPLISHED!")
                        return response['secret_message']
                
                if response['completed']:
                    print("\n🏁 Session completed!")
                    break
            
            # Final status
            final_result = await self.server.get_session_status({"session_id": self.session_id})
            final_status = json.loads(final_result[0].text)
            
            if final_status.get('secret_revealed'):
                print(f"🎉 Final result: SECRET REVEALED - '{final_status.get('secret_message', '')}'")
                return final_status.get('secret_message')
            else:
                print(f"😔 Mission failed: Only got {final_status['correct_answers']}/{final_status['min_correct']} correct")
                return None
                
        except Exception as e:
            print(f"❌ Agent error: {e}")
            return None
    
    async def solve_puzzle(self, puzzle_text):
        """Solve a puzzle by extracting clues and finding answers"""
        print("🔍 Parsing puzzle clues...")
        
        # Extract clues from puzzle text
        clues = self.extract_clues(puzzle_text)
        print(f"📋 Found {len(clues)} clues")
        
        # Solve each clue
        letters = []
        for i, clue in enumerate(clues, 1):
            answer = self.solve_clue(clue)
            if answer:
                letter = answer[0].lower()
                letters.append(letter)
                print(f"   {i}. {clue[:50]}... → '{answer}' → '{letter}'")
            else:
                print(f"   {i}. {clue[:50]}... → UNKNOWN → '?'")
                letters.append('?')
        
        final_answer = ''.join(letters).replace('?', '')
        print(f"🔤 Assembled answer: '{final_answer}'")
        return final_answer
    
    def extract_clues(self, puzzle_text):
        """Extract individual clues from puzzle text"""
        clues = []
        lines = puzzle_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('•') or 'subdomain' in line.lower():
                clues.append(line)
        
        return clues
    
    def solve_clue(self, clue):
        """Solve an individual clue using domain knowledge"""
        clue_lower = clue.lower()
        
        # Look for domain indicators
        for domain, knowledge in self.domain_knowledge.items():
            if domain.replace(' ', '') in clue_lower.replace(' ', ''):
                # Look for specific terms in this domain
                for term, description in knowledge.items():
                    if any(keyword in clue_lower for keyword in description.split()):
                        return term
                
                # Fallback: look for direct mentions
                for term in knowledge.keys():
                    if term in clue_lower:
                        return term
        
        # Common academic terms
        common_terms = {
            'troy': 'iliad',
            'epic': 'iliad', 
            'siege': 'iliad',
            'social': 'sociology',
            'society': 'sociology',
            'class': 'stratification',
            'layer': 'stratification',
            'straight': 'line',
            'path': 'line',
            'geometric': 'line',
            'immersive': 'ethnography',
            'research': 'ethnography',
            'anthropologist': 'ethnography',
            'central': 'cpu',
            'processor': 'cpu',
            'computer': 'cpu',
            'proportional': 'ratio',
            'comparing': 'ratio',
            'quantities': 'ratio',
            'magnitude': 'vector',
            'direction': 'vector',
            'linear algebra': 'vector',
            'fairness': 'equity',
            'equal': 'equity',
            'opportunity': 'equity',
            'frequency': 'resonance',
            'energy': 'resonance',
            'oscillatory': 'resonance',
            'rotational': 'torque',
            'turning': 'torque',
            'force': 'torque',
            'area': 'integral',
            'curve': 'integral',
            'calculus': 'integral',
            'crust': 'tectonics',
            'planet': 'tectonics',
            'dynamic': 'tectonics',
            'seal': 'gasket',
            'joint': 'gasket',
            'leakage': 'gasket'
        }
        
        for keyword, answer in common_terms.items():
            if keyword in clue_lower:
                return answer
        
        return None  # Unknown clue

async def main():
    """Run the example agent"""
    agent = ExamplePuzzleAgent()
    secret = await agent.run_mission()
    
    if secret:
        print(f"\n🎊 SUCCESS! Agent retrieved the secret: '{secret}'")
        print("🤖 Agent has demonstrated successful MCP integration!")
    else:
        print("\n💻 Agent needs improvement in puzzle solving logic")
    
    return secret is not None

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n✅ External agent integration verified!")
            print("🚀 Ready for real external agents to connect!")
        else:
            print("\n⚠️  Agent logic needs refinement")
    except KeyboardInterrupt:
        print("\n\n🛑 Agent interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
