#!/usr/bin/env python3
"""
Generate SEO-optimized tech tutorials using Groq API.
Outputs Hugo-compatible markdown with proper frontmatter.
"""
import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    print("pip install groq")
    exit(1)

# --- Config ---
OUTPUT_DIR = Path(__file__).parent.parent / "content" / "posts"
TOPICS = {
    "python": [
        "Python list comprehensions",
        "asyncio for beginners",
        "FastAPI REST API tutorial",
        "pandas data analysis",
        "Python decorators explained",
        "type hints in Python",
        "Python context managers",
        "unit testing with pytest",
        "virtual environments guide",
        "Python generators and iterators",
        "SQLAlchemy ORM tutorial",
        "Pydantic data validation",
        "Python logging best practices",
        "argparse CLI tools",
        "Python packaging with pyproject.toml",
    ],
    "ai-ml": [
        "intro to machine learning",
        "neural networks from scratch",
        "Hugging Face transformers tutorial",
        "fine-tuning LLMs",
        "RAG pipeline tutorial",
        "LangChain basics",
        "vector databases explained",
        "prompt engineering guide",
        "image classification with PyTorch",
        "NLP sentiment analysis",
        "building AI agents",
        "Groq API tutorial",
        "embedding models comparison",
        "LLM evaluation metrics",
    ],
    "web-dev": [
        "HTML CSS basics",
        "JavaScript ES6 features",
        "React hooks tutorial",
        "Next.js app router",
        "Tailwind CSS guide",
        "REST API design",
        "GraphQL vs REST",
        "Web authentication JWT",
        "CSS grid layout",
        "TypeScript for beginners",
        "Vite build tool",
        " Progressive Web Apps",
        "WebSocket tutorial",
        "Docker for web developers",
    ],
    "devops": [
        "Docker basics",
        "Kubernetes introduction",
        "GitHub Actions CI CD",
        "Linux command line",
        "nginx reverse proxy",
        "AWS EC2 tutorial",
        "Terraform basics",
        "Prometheus monitoring",
        "bash scripting guide",
        "SSH tunneling",
        "Git branching strategies",
        "PostgreSQL tutorial",
        "Redis caching guide",
        "SSL TLS certificates",
    ],
}

# SEO keyword templates
SEO_TEMPLATES = {
    "python": "python tutorial, {topic}, learn python, python for beginners, {topic} guide",
    "ai-ml": "machine learning tutorial, {topic}, AI tutorial, {topic} guide, artificial intelligence",
    "web-dev": "web development tutorial, {topic}, {topic} guide, frontend development",
    "devops": "devops tutorial, {topic}, {topic} guide, system administration",
}

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY not set")
        exit(1)
    return Groq(api_key=api_key)

def generate_article(client, topic, category):
    """Generate a full SEO-optimized article using Groq."""
    seo_keywords = SEO_TEMPLATES[category].format(topic=topic)
    
    prompt = f"""Write a comprehensive, SEO-optimized tech tutorial about: {topic}

REQUIREMENTS:
1. Title: Clear, includes main keyword, under 60 characters
2. Meta description: 150-160 characters, includes keywords, compelling
3. Structure: Use H2 (##) and H3 (###) headings naturally
4. Length: 1500-2500 words
5. Include: Code examples (Python/bash/JS as appropriate), explanations, best practices
6. Tone: Friendly, beginner-to-intermediate, practical
7. SEO: Naturally include these keywords: {seo_keywords}
8. Add a "Key Takeaways" section at the end
9. Use markdown formatting: code blocks, lists, bold, blockquotes

OUTPUT FORMAT (strict JSON):
{{
    "title": "article title (under 60 chars)",
    "description": "meta description (150-160 chars)",
    "tags": ["tag1", "tag2", "tag3"],
    "content": "full markdown article content"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )
    
    return json.loads(response.choices[0].message.content)

def slugify(text):
    """Convert text to URL-friendly slug."""
    return text.lower().strip().replace(" ", "-").replace("/", "-")

def save_article(article, category):
    """Save article as Hugo markdown with frontmatter."""
    today = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(article["title"])
    filename = f"{today}-{slug}.md"
    filepath = OUTPUT_DIR / filename
    
    tags_yaml = json.dumps(article.get("tags", [category]))
    
    frontmatter = f"""---
title: "{article['title']}"
date: {today}
draft: false
description: "{article['description']}"
tags: {tags_yaml}
categories: ["{category.replace('-', '/').title()}"]
author: "{os.environ.get('BLOG_AUTHOR', 'Tech Tutorials Hub')}"
---"""
    
    content = f"{frontmatter}\n\n{article['content']}"
    filepath.write_text(content, encoding="utf-8")
    print(f"  -> {filename}")
    return filepath

def main():
    client = get_groq_client()
    num_articles = int(os.environ.get("NUM_ARTICLES", "3"))
    
    print(f"Generating {num_articles} articles...")
    generated = []
    
    # Spread across categories
    categories = list(TOPICS.keys())
    
    for i in range(num_articles):
        category = categories[i % len(categories)]
        topic = random.choice(TOPICS[category])
        
        print(f"\n[{i+1}/{num_articles}] {category}: {topic}")
        
        try:
            article = generate_article(client, topic, category)
            path = save_article(article, category)
            generated.append({
                "title": article["title"],
                "category": category,
                "file": str(path),
            })
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Write summary for GitHub Actions
    summary_path = OUTPUT_DIR.parent.parent / "generation-summary.json"
    summary_path.write_text(json.dumps(generated, indent=2), encoding="utf-8")
    
    print(f"\nDone! Generated {len(generated)} articles.")
    
    # Print for GitHub Step Summary
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write("## Generated Articles\n\n")
            for g in generated:
                f.write(f"- **{g['title']}** ({g['category']})\n")

if __name__ == "__main__":
    main()
