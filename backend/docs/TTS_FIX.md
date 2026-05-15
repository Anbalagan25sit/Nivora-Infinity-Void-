# TTS Thinking Tags Fix - COMPLETE SOLUTION

## 🐛 The Problem

**Error:**
```
livekit.agents._exceptions.APIError: no audio frames were pushed for text: 
<thinking> The user has requested to see their screen... </thinking>
```

**Root Cause:**
- AWS Nova Pro LLM was outputting `<thinking>` tags in its responses
- ElevenLabs TTS cannot synthesize XML-like tags
- This caused the TTS to fail with "no audio frames were pushed"

---

## ✅ The Complete Fix (3 Layers)

### Layer 1: **Strengthened System Prompts** (Prevention)

Updated both `prompts.py` (Nivora) and `infin_prompts.py` (Infin) with explicit instructions:

```python
CRITICAL - THIS IS A VOICE-ONLY INTERFACE:
- You are speaking out loud via text-to-speech. The user HEARS your response.
- NEVER output <thinking>, <reflection>, or ANY XML-like tags. They cannot be spoken.
- NEVER explain your reasoning process. Just give the answer.
- NEVER say "I am thinking", "Let me think", "One moment", etc.
- Direct, immediate responses only. No internal monologue.
- No markdown. No asterisks. No emojis. No formatting. Pure speech.
- If you need to use a tool, call it silently and respond with the result.
```

### Layer 2: **Reduced Temperature** (Focus)

Changed LLM temperature from `0.8` to `0.7` for more focused, deterministic responses:

```python
llm=aws.LLM(
    model=bedrock_model(),
    temperature=0.7,  # More focused, less creative rambling
    region=aws_region(),
)
```

### Layer 3: **Response Filtering** (Safeguard)

Added automatic tag stripping in `generic_agent.py` as a failsafe:

```python
def strip_thinking_tags(text: str) -> str:
    """Remove XML-like tags that TTS cannot speak."""
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<reflection>.*?</reflection>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<reasoning>.*?</reasoning>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # ... more tag removal
    return text.strip()

class GenericAgent(Agent):
    async def generate_reply(self, *args, **kwargs):
        response = await super().generate_reply(*args, **kwargs)
        if response and hasattr(response, 'content'):
            response.content = strip_thinking_tags(response.content)
        return response
```

**This ensures that even if the LLM ignores instructions, the tags are automatically removed before reaching TTS!**

---

## 🎯 Why This Happens

AWS Nova Pro (and many frontier LLMs) are trained to show reasoning with `<thinking>` tags for better transparency. However:

- ✅ **Good for text chat** - Users can see the reasoning process
- ❌ **Bad for voice** - TTS cannot speak XML tags

The 3-layer fix ensures the LLM understands it's in a **voice-only context** where thinking tags are inappropriate, and removes them automatically if they slip through.

---

## 🧪 Testing

After the fix, test with screen share:

```
You: "Look at my screen"
Agent: [Silently calls describe_screen_share tool]
       "I see your VSCode window with..."
```

**NOT:**
```
Agent: "<thinking>I need to use the describe_screen_share tool</thinking>"
       [TTS ERROR: no audio frames]
```

If you see this warning in logs:
```
Filtered thinking tags from response: <thinking>...
```

That means Layer 3 (response filtering) caught and removed the tags automatically!

---

## 📝 Files Modified

- ✅ `prompts.py` - Updated Nivora instructions (Layer 1)
- ✅ `infin_prompts.py` - Updated Infin instructions (Layer 1)
- ✅ `multi_agent_livekit.py` - Reduced temperature to 0.7 (Layer 2)
- ✅ `generic_agent.py` - Added response filtering (Layer 3)

---

## 🛡️ Defense in Depth

The 3-layer approach ensures reliability:

1. **Prevention** (Layer 1): Tell LLM not to use thinking tags
2. **Focus** (Layer 2): Lower temperature for more controlled output  
3. **Safeguard** (Layer 3): Automatically strip tags if they appear

**Even if one layer fails, the others provide protection!**

---

## ✅ Expected Behavior Now

```
User: "Look at my screen"
  ↓
Infin LLM thinks: (internally) "User wants screen analysis"
  ↓
[Layer 1: LLM respects instructions, doesn't output <thinking> tags]
  ↓
Infin calls: describe_screen_share("What is visible on the user's screen?")
  ↓
Tool returns: "I see a VSCode window with Python code..."
  ↓
Infin generates: "I see your VSCode window with Python code and an error on line 47."
  ↓
[Layer 3: Filter checks response - no tags found, passes through]
  ↓
TTS speaks: ✅ "I see your VSCode window with Python code and an error on line 47."
```

**No `<thinking>` tags = No TTS errors!**

---

## 🔍 Monitoring

Check logs for these indicators:

**✅ Good:**
```
Voice switched to Nivora: cgSgspJ2msm6clMCkdW9
Multi-agent session started with Infin
```

**⚠️ Filter Active (but working):**
```
Filtered thinking tags from response: <thinking>...
```
*This means Layer 3 is protecting you - the fix is working!*

**❌ Still broken (shouldn't happen):**
```
livekit.agents._exceptions.APIError: no audio frames were pushed
```
*If this still occurs, the response filter might not be intercepting correctly.*

---

## 🎉 Summary

The 3-layer fix ensures AWS Nova Pro works perfectly in voice mode:

✅ **Layer 1 (Instructions):** LLM understands voice context
✅ **Layer 2 (Temperature):** More focused, less rambling  
✅ **Layer 3 (Filtering):** Automatic tag removal as failsafe

**The multi-agent system should now work smoothly without TTS errors!** 🚀

---

## 🔧 If You Need to Disable Filtering

If for some reason you want to disable the automatic filtering:

```python
# In generic_agent.py
class GenericAgent(Agent):
    # Comment out or remove the generate_reply override
    # async def generate_reply(self, *args, **kwargs):
    #     ...
```

But this is **not recommended** - the filter is a safety net!

