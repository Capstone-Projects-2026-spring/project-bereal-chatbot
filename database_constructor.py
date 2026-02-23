import csv
import json
import os
import time
from typing import List, Dict, Set
from anthropic import Anthropic

#WARNING:  SAVE SYSTEM NOT IMPLEMENTED, IF SCRIPT CRASHES YOU  WILL LOSE RESULTS AND TOKENS SPENT.  (SHOULD TEST WITH SMALL BATCH FIRST)


anthropic_key = "ENTER API KEY HERE"
output_file = "vibecheck_prompts.csv"
total_prompts = 10000
batch_size = 50  # bigger batches results in less API calls
max_retries = 3
retry_delay = 2

allowed_tags = {
    "sports", "tv_movies", "food", "would_you_rather",
    "personal_life", "work_life", "hobbies", "random_fun"
}

response_types = {"text", "image"}

class PromptGenerator:
    
    def __init__(self, api_key: str = None):
        self.client = Anthropic(api_key=api_key or os.environ.get("anthropic_key"))
        self.generated_prompts: Set[str] = set()
        self._load_existing_prompts()
        
    def _load_existing_prompts(self):
        if not os.path.exists(output_file):
            return
        
        with open(output_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.generated_prompts.add(row["prompt"].lower())
        
    def create_generation_prompt(self, batch_num: int, batch_size: int) -> str:
        # prompt being fed to claude is below 
        return f"""Generate {batch_size} conversation-starting prompts for a workplace community app. These prompts help new employees connect with coworkers and make outsiders feel like insiders.

Goal: Start genuine conversations, not just get one-word answers. People should feel excited to respond and learn about each other.

Make them:
- Interesting enough that people actually want to answer
- Personal but not invasive
- Fun, creative, unexpected
- Good conversation starters (avoid yes/no questions)
- Mix of lighthearted and thought-provoking

Prompt types:
- "text": Questions that spark stories or opinions
- "image": Photo requests that show personality

Tags: 1-2 from [sports, tv_movies, food, would_you_rather, personal_life, work_life, hobbies, random_fun]

Good examples:
- "What's a skill you have that would be totally useless in a zombie apocalypse?"
- "Show us the last photo you took on your phone!"
- "If your morning commute had a soundtrack, what song would it be?"
- "What's something you're unreasonably competitive about?"

Bad examples (too boring):
- "What's your favorite color?"
- "Do you like coffee?"
- "How was your weekend?"

Workplace safe: No politics, religion, salary, health issues,  or anything too personal.

Return JSON only:
[
  {{"prompt": "question here", "response_type": "text", "tags": ["tag1"]}},
  ...
]"""
    
    def generate_batch(self, batch_num: int, batch_size: int) -> List[Dict]:
        print(f"Batch {batch_num}: Requesting {batch_size} prompts...")
        for attempt in range(max_retries):
            try:
                message = self.client.messages.create(
                    model="claude-3-haiku-20240307",  # haiku is way cheaper
                    max_tokens=4000,
                    temperature=1.0,
                    messages=[{
                        "role": "user",
                        "content": self.create_generation_prompt(batch_num, batch_size)
                    }]
                )
                
                response_text = message.content[0].text.strip()
                
                # claude sometimes wraps stuff in markdown
                if response_text.startswith("```"):
                    lines = response_text.split("\n")
                    response_text = "\n".join(lines[1:-1])
                
                prompts_data = json.loads(response_text)
                valid_prompts = self._validate_batch(prompts_data)
                
                if valid_prompts:
                    print(f"Batch {batch_num}: Got {len(valid_prompts)} valid prompts")
                    return valid_prompts
                else:
                    print(f"Batch {batch_num}: No valid prompts, retrying...")
                    
            except json.JSONDecodeError as e:
                print(f"Batch {batch_num}, Attempt {attempt + 1}: JSON parse error - {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    
            except Exception as e:
                print(f"Batch {batch_num}, Attempt {attempt + 1}: Error - {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        return []
    
    def _validate_batch(self, prompts_data: List[Dict]) -> List[Dict]:
        # make sure prompts are actually good
        valid_prompts = []
        
        for item in prompts_data:
            try:
                
                if not all(k in item for k in ["prompt", "response_type", "tags"]):
                    continue
                
                prompt_text = item["prompt"].strip()
                response_type = item["response_type"].lower()
                tags = item["tags"]
                
                if response_type not in response_types:
                    continue
                
                if not isinstance(tags, list) or len(tags) == 0 or len(tags) > 2:
                    continue
                
                if not all(tag in allowed_tags for tag in tags):
                    continue
                
                # skip duplicates
                if prompt_text.lower() in self.generated_prompts:
                    continue
                
                if len(prompt_text) < 10 or len(prompt_text) > 300:
                    continue
                
                valid_prompts.append({
                    "prompt": prompt_text,
                    "response_type": response_type,
                    "tags": tags
                })
                
                self.generated_prompts.add(prompt_text.lower())
                
            except Exception as e:
                print(f"Validation error for prompt: {e}")
                continue
        
        return valid_prompts
    
    def generate_all_prompts(self, total: int) -> List[Dict]:
        all_prompts = []
        batch_num = 1
        
        print(f"Starting generation of {total} prompts...")
        
        while len(all_prompts) < total:
            remaining = total - len(all_prompts)
            current_batch_size = min(batch_size, remaining)
            
            print(f"\nBatch {batch_num}: Requesting {current_batch_size} prompts...")
            
            batch_prompts = self.generate_batch(batch_num, current_batch_size)
            
            if batch_prompts:
                all_prompts.extend(batch_prompts)
                print(f"Progress: {len(all_prompts)}/{total} prompts generated")
            else:
                print(f"Batch {batch_num}: Failed to generate prompts")
            
            batch_num += 1
            time.sleep(1)
        
        return all_prompts[:total]


def get_next_prompt_id(filename: str) -> int:
    if not os.path.exists(filename):
        return 1
    
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        if not rows:
            return 1
        return int(rows[-1]["prompt_id"]) + 1


def write_to_csv(prompts: List[Dict], filename: str):
    file_exists = os.path.exists(filename)
    next_id = get_next_prompt_id(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['prompt_id', 'prompt', 'response_type', 'tags', 'times_asked', 'times_responded']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for i, prompt_data in enumerate(prompts):
            writer.writerow({
                'prompt_id': next_id + i,
                'prompt': prompt_data['prompt'],
                'response_type': prompt_data['response_type'],
                'tags': ','.join(prompt_data['tags']),
                'times_asked': 0,
                'times_responded': 0
            })


def main():
    print("=" * 50)
    print("Slack Prompt Generator")
    print("=" * 50)
    
    
    generator = PromptGenerator(anthropic_key)
    
    start_time = time.time()
    prompts = generator.generate_all_prompts(total_prompts)
    elapsed_time = time.time() - start_time
    
    write_to_csv(prompts, output_file)
    
    print(f"\nDONE! Generated {len(prompts)} prompts")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()