"""
AIEAT Prompt Builder - Builds translation prompts from style settings.

Refactored for Instruction-Tuned Models (Typhoon/Llama 3).
Features:
- Thai Universal Template (guarantees Thai output)
- Dynamic Role Mapping (DB Output Type -> Competency)
- Strict Anti-Transliteration Rules (Lisa Su, Nvidia)
"""
import json
from typing import Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


def build_translation_prompt(style: Dict, article: Dict) -> str:
    """
    Build translation prompt using Thai Universal Template.
    Maps DB 'output_type' to a specific professional competency.
    """
    # 1. Map DB Fields to Competency Roles
    output_type = style.get('output_type', 'facebook').lower()
    tone_key = style.get('tone', 'conversational').lower()
    
    # ROLE MAPPING (The "Reflect DB but Universal" Logic)
    role_map = {
        'facebook': 'ผู้เชี่ยวชาญด้านคอนเทนต์โซเชียลมีเดีย (Social Media Content Expert)',
        'web article': 'นักข่าวและบรรณาธิการมืออาชีพ (Professional Journalist)',
        'summary': 'ผู้เชี่ยวชาญด้านการสรุปความ (Executive Summarizer)'
    }
    # Fallback to general expert if type is unknown
    role = role_map.get(output_type, 'ผู้เชี่ยวชาญด้านการแปลและเรียบเรียงเนื้อหา')

    # TONE MAPPING
    tone_map = {
        'conversational': 'เป็นกันเอง สนุกสนาน เข้าถึงง่าย (Conversational)',
        'professional': 'ทางการ น่าเชื่อถือ กระชับ (Professional)',
        'academic': 'วิชาการ เชิงลึก (Academic)'
    }
    tone_desc = tone_map.get(tone_key, tone_key)

    # 2. Extract Flags & Settings
    custom_instr = (style.get('custom_instructions') or '').strip()
    include_lead = style.get('include_lead', 1)
    include_analysis = style.get('include_analysis', 1)
    include_source = style.get('include_source', 1)
    include_keywords = style.get('include_keywords', 1)
    include_hashtags = style.get('include_hashtags', 0)
    
    # Length Logic
    length_map = {
        'short': 'สั้นกระชับ (Short)',
        'medium': 'ปานกลาง (Medium)',
        'long': 'ยาวละเอียด (Long)'
    }
    hl_len = length_map.get(style.get('headline_length', 'medium'), 'ปานกลาง')
    body_len = length_map.get(style.get('body_length', 'medium'), 'ปานกลาง')

    # 3. Build The Universal Structure
    
    # SECTION 1: ROLE & OBJECTIVE (Thai)
    context_section = f"""[บทบาทและหน้าที่ (Role & Objective)]
คุณคือ **{role}**
หน้าที่ของคุณคือ: แปลและเรียบเรียงบทความภาษาอังกฤษเป็นภาษาไทย (Thai) ให้มีความลื่นไหล เป็นธรรมชาติ และถูกต้องแม่นยำ เหมาะสมกับรูปแบบงาน: "{output_type}" """

    # SECTION 2: TONE & STYLE
    tone_section = f"""
[โทนและสไตล์ (Tone & Style)]
โทนภาษา: {tone_desc}
สไตล์: เขียนให้เหมือนเจ้าของภาษา (Native Thai) หลีกเลี่ยงสำนวนแปลตรงตัว (Translate meaning, not just words)"""

    # SECTION 3: STRICT RULES (Anti-Transliteration)
    constraints_section = f"""
[กฎระเบียบสำคัญ (Strict Rules)]
ต้องปฏิบัติตามกฎเหล่านี้อย่างเคร่งครัด:

1. **ห้ามแต่งเติมข้อมูล (No Hallucinations):** 
   - แปลเฉพาะข้อมูลที่มีในต้นฉบับเท่านั้น ห้ามสุ่มเดาความหมาย
   - คำศัพท์ทางเทคนิค (Tech Terms เช่น Context Window, Parameters, MoE) ให้แปลตามบริบทของ Computer Science หรือใช้คำทับศัพท์ภาษาอังกฤษ หากแปลไทยแล้วเสียความหมาย

2. **ห้ามแปลชื่อเฉพาะ (No Transliteration of Proper Nouns):**
   - ให้คงรูปภาษาอังกฤษต้นฉบับไว้เสมอ ห้ามอ่านออกเสียงเป็นไทย:
   - **ชื่อบริษัท/แบรนด์**: ใช้ "Nvidia" (ห้าม "นีวิดีอา"), "Google", "OpenAI"
   - **ชื่อบุคคล**: ใช้ "Lisa Su", "Sam Altman"
   - **ศัพท์เทคนิค**: ใช้ "GPU", "Generative AI", "Tokens"
{f'   - {custom_instr}' if custom_instr else ''}"""

    # SECTION 4: OUTPUT FORMAT
    analysis_block = """
## วิเคราะห์
(วิเคราะห์ผลกระทบหรือความสำคัญ 2-3 ข้อ)""" if include_analysis else ""

    format_section = f"""
[รูปแบบการตอบ (Output Format in Markdown)]
บังคับให้ตอบด้วยโครงสร้าง Markdown ด้านล่างนี้ ห้ามพิมพ์คำว่า "หัวข้อข่าว" หรือ "เนื้อหาข่าว" ออกมาเป็น Header เด็ดขาด:

# (พิมพ์หัวข้อข่าวที่น่าสนใจ ความยาว {hl_len})
{'> (พิมพ์บทนำ/Lead Paragraph สรุปใจความสำคัญ)' if include_lead else ''}

(พิมพ์เนื้อหาข่าวที่เรียบเรียงใหม่โดยละเอียด ความยาว {body_len})
{analysis_block}

---
{f'Keywords: [คำสำคัญภาษาไทย 3-5 คำ]' if include_keywords else ''}
{f'Hashtags: #แท็ก1 #แท็ก2 #แท็ก3' if include_hashtags else ''}
{f'Source: [ชื่อแหล่งที่มา]' if include_source else ''}
"""

    # SECTION 5: INPUT
    input_section = f"""
[ข้อมูลนำเข้า (Input Data)]
Title: {article.get('headline', '')}

{article.get('content', '')}
"""

    return f"{context_section}\n{tone_section}\n{constraints_section}\n{format_section}\n{input_section}"


def parse_translation_response(text: str) -> Dict:
    """
    Parse LLM response (supports Markdown format).
    Robust wrapper around parse_markdown_format.
    """
    return parse_markdown_format(text)


def parse_markdown_format(text: str) -> Dict:
    """
    Robust Markdown parser for the new prompt format.
    """
    result = {
        'Keywords': '',
        'Headline': '',
        'Lead': '',
        'Body': '',
        'Analysis': '',
        'Source': '',
        'Hashtags': '',
        'success': False
    }
    
    try:
        # Split by Metadata separator (---)
        parts = text.split('---')
        content_part = parts[0].strip()
        metadata_part = parts[1].strip() if len(parts) > 1 else ""
        
        # 1. Headline (Starting with #)
        headline_match = re.search(r'^#\s*(.+)$', content_part, re.MULTILINE)
        if headline_match:
            result['Headline'] = headline_match.group(1).strip()
            content_part = content_part.replace(headline_match.group(0), '').strip()
            
        # 2. Lead (Blockquote >)
        lead_match = re.search(r'^>\s*(.+)$', content_part, re.MULTILINE)
        if lead_match:
            result['Lead'] = lead_match.group(1).strip()
            content_part = content_part.replace(lead_match.group(0), '').strip()
            
        # 3. Analysis (Header ##)
        analysis_patterns = [r'^##\s*(Analysis|วิเคราะห์|วิเคราะห์ผลกระทบ|ผลกระทบ|Impact)(.*?)(?=^##|\Z)']
        for pattern in analysis_patterns:
            analysis_match = re.search(pattern, content_part, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            if analysis_match:
                result['Analysis'] = analysis_match.group(2).strip()
                content_part = content_part.replace(analysis_match.group(0), '').strip()
                break
            
        # 4. Body (Remainder)
        result['Body'] = content_part.strip()
        
        # 5. Metadata
        if metadata_part:
            kw_match = re.search(r'(Keywords|คีย์เวิร์ด)[:\s]*(.+?)(?=\n|$)', metadata_part, re.IGNORECASE)
            if kw_match: result['Keywords'] = kw_match.group(2).strip()
            
            src_match = re.search(r'(Source|ที่มา|แหล่งที่มา)[:\s]*(.+?)(?=\n|$)', metadata_part, re.IGNORECASE)
            if src_match: result['Source'] = src_match.group(2).strip()
            
            hash_match = re.search(r'(Hashtags|แฮชแท็ก)[:\s]*(.+?)(?=\n|$)', metadata_part, re.IGNORECASE)
            if hash_match: result['Hashtags'] = hash_match.group(2).strip()
                
        if result['Body'] or result['Headline']:
            result['success'] = True
            
    except Exception as e:
        logger.error(f"Parser Error: {e}")
        result['Body'] = text
        result['success'] = True
        
    return result

# Default presets (kept for compatibility)
DEFAULT_PRESETS = {
    'facebook': {
        'name': 'Facebook Post',
        'output_type': 'facebook',
        'persona': 'Social Media Expert', 
        'tone': 'conversational',
        'include_hashtags': 1,
        'is_active': 1
    }
}
