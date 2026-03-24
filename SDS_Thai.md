# เอกสารข้อกำหนดการออกแบบซอฟต์แวร์ (Software Design Specification)
# ระบบ AIEAT News Dashboard

**เวอร์ชัน:** 1.0  
**วันที่:** 23 มีนาคม 2569  
**ผู้จัดทำ:** ทีมพัฒนา AIEAT  

---

## สารบัญ

1. [บทนำ (Introduction)](#1-บทนำ-introduction)
2. [ภาพรวมระบบ (System Overview)](#2-ภาพรวมระบบ-system-overview)
3. [โครงสร้างโปรเจกต์ (Project Structure)](#3-โครงสร้างโปรเจกต์-project-structure)
4. [การออกแบบฐานข้อมูล (Database Design)](#4-การออกแบบฐานข้อมูล-database-design)
5. [การออกแบบส่วนประกอบ (Component Design)](#5-การออกแบบส่วนประกอบ-component-design)
6. [การติดตั้งและ Deployment](#6-การติดตั้งและ-deployment)
7. [ข้อจำกัดและแนวทางพัฒนาต่อ (Limitations & Future Work)](#7-ข้อจำกัดและแนวทางพัฒนาต่อ-limitations--future-work)

---

## 1. บทนำ (Introduction)

### 1.1 วัตถุประสงค์ของระบบ

AIEAT News Dashboard เป็น**ระบบกระดานข่าวอัจฉริยะ**ที่ออกแบบมาให้ทำงานบนเครื่องของผู้ใช้ 100% โดยไม่จำเป็นต้องเชื่อมต่อกับ Cloud Service ใดๆ ระบบนี้ถูกพัฒนาขึ้นเพื่อตอบโจทย์องค์กรที่ต้องการ:

- **ความเป็นส่วนตัวของข้อมูล** — ข้อมูลทั้งหมดถูกประมวลผลและจัดเก็บในเครื่องของผู้ใช้เท่านั้น ไม่มีการส่งข้อมูลไปยัง Server ภายนอก
- **ความเป็นอิสระจาก Internet** — หลังจากดึงข่าวมาแล้ว ผู้ใช้สามารถอ่าน วิเคราะห์ และแปลข่าวได้โดยไม่ต้องเชื่อมต่อ Internet
- **การปรับแต่งตามความต้องการ** — ผู้ใช้สามารถกำหนด Keyword, แหล่งข่าว และรูปแบบการแปลได้อย่างอิสระ
- **ต้นทุนต่ำ** — ไม่มีค่าใช้จ่ายรายเดือนสำหรับ Cloud API เพราะใช้ AI Model ที่รันบนเครื่องท้องถิ่น

### 1.2 ขอบเขตของระบบ

ระบบ AIEAT ครอบคลุมฟังก์ชันการทำงานหลัก 4 ประการ:

| ฟังก์ชัน | รายละเอียด |
|---------|------------|
| **ดึงข่าวอัตโนมัติ** | ดึงบทความจากเว็บไซต์ข่าวที่ผู้ใช้กำหนดไว้ รองรับทั้ง RSS Feed และการดึงจาก HTML โดยตรง |
| **ให้คะแนนความเกี่ยวข้อง** | ใช้ AI ประเมินว่าข่าวแต่ละชิ้นเกี่ยวข้องกับ Keyword ที่ผู้ใช้สนใจมากน้อยเพียงใด (คะแนน 1-10) |
| **แปลภาษา** | แปลบทความภาษาอังกฤษเป็นภาษาไทยโดยอัตโนมัติ พร้อมปรับรูปแบบการเขียนตามที่ผู้ใช้กำหนด |
| **จัดการโปรไฟล์** | รองรับหลายโปรไฟล์ผู้ใช้ แต่ละโปรไฟล์มี Keyword และความสนใจที่แตกต่างกัน |

### 1.3 คำจำกัดความและศัพท์เทคนิค

| คำศัพท์ | ความหมาย |
|--------|----------|
| **Scraper** | โปรแกรมที่ทำหน้าที่ดึงข้อมูลจากเว็บไซต์โดยอัตโนมัติ ในระบบนี้ใช้สำหรับดึงบทความข่าวจากแหล่งข่าวต่างๆ |
| **Ollama** | แพลตฟอร์มสำหรับรัน Large Language Model (LLM) บนเครื่องท้องถิ่น รองรับ Model หลากหลายรูปแบบ ทำงานผ่าน HTTP API ที่ port 11434 |
| **Typhoon 2.5** | โมเดลภาษาไทยที่พัฒนาโดย SCB 10X มีความสามารถในการเข้าใจและสร้างข้อความภาษาไทยได้อย่างเป็นธรรมชาติ รุ่นที่ใช้คือ `scb10x/typhoon2.5-qwen3-4b:latest` |
| **Profile** | ชุดการตั้งค่าที่รวม Keyword และ Domain ที่ผู้ใช้สนใจ ระบบรองรับหลาย Profile เพื่อแยกความสนใจในหัวข้อต่างๆ |
| **Style** | รูปแบบการแสดงผลของ AI กำหนดโทนการเขียน ความยาว และองค์ประกอบที่ต้องการในผลลัพธ์การแปล |
| **RSS Feed** | รูปแบบมาตรฐานสำหรับเผยแพร่ข่าวสารในรูปแบบ XML ทำให้ดึงข่าวได้ง่ายและเป็นระบบ |
| **url_hash** | ค่า Hash ของ URL ที่ใช้ตรวจสอบว่าบทความนี้เคยถูกดึงมาแล้วหรือไม่ ป้องกันการเก็บบทความซ้ำ |
| **Flet** | Framework สำหรับสร้าง Desktop Application ด้วย Python มีรูปแบบการเขียนคล้าย Flutter |

---

## 2. ภาพรวมระบบ (System Overview)

### 2.1 สถาปัตยกรรมแบบ Local-first

ระบบ AIEAT ถูกออกแบบตามหลักการ **Local-first Architecture** ซึ่งหมายความว่า:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        เครื่องของผู้ใช้ (User's Machine)                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    AIEAT Application                             │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │   │
│  │  │  Flet UI  │  │  Backend  │  │  SQLite   │  │  Ollama   │    │   │
│  │  │  (Pages)  │◄─►│  Services │◄─►│ Database │  │  Engine   │    │   │
│  │  └───────────┘  └─────┬─────┘  └───────────┘  └─────▲─────┘    │   │
│  │                       │                              │          │   │
│  │                       │         HTTP API             │          │   │
│  │                       │      localhost:11434         │          │   │
│  │                       └──────────────────────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Ollama Server (Local)                         │   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │  Typhoon 2.5 Model (scb10x/typhoon2.5-qwen3-4b:latest)  │    │   │
│  │  └─────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS (เฉพาะตอนดึงข่าว)
                                    ▼
                    ┌───────────────────────────────────┐
                    │     เว็บไซต์ข่าวภายนอก            │
                    │  (TechCrunch, Reuters, etc.)      │
                    └───────────────────────────────────┘
```

**หลักการสำคัญ:**

1. **ไม่มี Cloud Dependency** — ไม่ต้องลงทะเบียน ไม่ต้องมี API Key จากบริการภายนอก
2. **ข้อมูลอยู่ในเครื่องเสมอ** — ฐานข้อมูล SQLite และการตั้งค่าทั้งหมดอยู่ใน Local Storage
3. **AI ทำงานบนเครื่อง** — Ollama + Typhoon 2.5 รันบน localhost ไม่ส่งข้อมูลไปประมวลผลบน Cloud
4. **เชื่อมต่อ Internet เฉพาะตอนดึงข่าว** — หลังจากดึงข่าวมาแล้ว ทุกอย่างทำงานได้แบบ Offline

### 2.2 Data Flow

การไหลของข้อมูลในระบบ AIEAT มี 5 ขั้นตอนหลัก:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   ขั้นตอน 1   │    │   ขั้นตอน 2   │    │   ขั้นตอน 3   │    │   ขั้นตอน 4   │    │   ขั้นตอน 5   │
│              │    │              │    │              │    │              │    │              │
│ User Config  │───►│   Scraper    │───►│   Database   │───►│  AI Scoring  │───►│  Dashboard   │
│              │    │              │    │              │    │              │    │              │
│ - Keywords   │    │ - RSS/HTML   │    │ - Store      │    │ - Score 1-10 │    │ - Display    │
│ - Sources    │    │ - Extract    │    │ - Dedupe     │    │ - Translate  │    │ - Filter     │
│ - Profiles   │    │ - Filter     │    │ - Index      │    │ - Tag Match  │    │ - Sort       │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

**รายละเอียดแต่ละขั้นตอน:**

| ขั้นตอน | Input | Process | Output |
|--------|-------|---------|--------|
| **1. User Config** | การตั้งค่าจากผู้ใช้ | ผู้ใช้กำหนด Keywords, แหล่งข่าว, และ Profile ที่ต้องการใช้งาน | Configuration ใน SQLite |
| **2. Scraper** | URLs ของแหล่งข่าว | ดึง RSS/HTML, Extract เนื้อหา, กรอง Duplicate และ Paywall | Raw Articles |
| **3. Database** | Raw Articles | บันทึกลง articles_meta + article_content, สร้าง url_hash | Stored Articles |
| **4. AI Scoring** | Article + Keywords | ส่งเนื้อหาให้ Typhoon วิเคราะห์ความเกี่ยวข้องและแปลภาษา | Scored + Translated Articles |
| **5. Dashboard** | Processed Articles | แสดงผลบน UI, กรองตาม Score/Status, เรียงลำดับ | User-readable News Feed |

### 2.3 ตารางเทคโนโลยี

| ชั้น (Layer) | เทคโนโลยี | เวอร์ชัน | หน้าที่ |
|-------------|----------|---------|--------|
| **Runtime** | Python | 3.10+ | ภาษาหลักของโปรเจกต์ |
| **UI Framework** | Flet | 0.21+ | สร้าง Desktop GUI แบบ Cross-platform |
| **Database** | SQLite | 3.x | ฐานข้อมูลท้องถิ่น ไม่ต้องติดตั้งแยก |
| **AI Runtime** | Ollama | Latest | แพลตฟอร์มสำหรับรัน LLM บนเครื่องท้องถิ่น |
| **AI Model** | Typhoon 2.5 | qwen3-4b | โมเดลภาษาไทยสำหรับ Scoring และ Translation |
| **HTTP Client** | aiohttp | 3.9+ | Async HTTP สำหรับดึงข่าวและเรียก Ollama API |
| **Content Extraction** | trafilatura | 1.6+ | ดึงเนื้อหาหลักจาก HTML (Primary) |
| **Content Extraction** | newspaper3k | 0.2+ | ดึงเนื้อหาหลักจาก HTML (Fallback) |
| **Build Tool** | PyInstaller | 6.x | สร้าง Standalone Executable |
| **Installer** | InnoSetup | 6.x | สร้าง Windows Installer (.exe) |

---

## 3. โครงสร้างโปรเจกต์ (Project Structure)

### 3.1 แผนผังไดเรกทอรี

```
AIEAT_Internship/
├── app/                            # แพ็กเกจหลักของแอปพลิเคชัน
│   ├── __init__.py                 # ทำให้ app เป็น Python package
│   ├── config/                     # ไดเรกทอรีสำหรับการตั้งค่า
│   │   └── settings.py             # (ว่าง — config อยู่ใน JSON และ Database)
│   ├── services/                   # ชั้น Backend Logic
│   │   ├── ai_engine.py            # Wrapper สำหรับ Ollama AI inference
│   │   ├── backend_api.py          # Facade Pattern — จุดเข้าถึงเดียวสำหรับ Backend
│   │   ├── database_manager.py     # CRUD Operations ทั้งหมดสำหรับ SQLite
│   │   ├── ollama_engine.py        # HTTP Client สำหรับ Ollama API
│   │   ├── prompt_builder.py       # สร้าง Prompt จาก Style settings
│   │   └── scraper_service.py      # Async News Scraper (aiohttp)
│   ├── ui/                         # ชั้น Frontend (Flet Framework)
│   │   ├── components/             # UI Components ที่ใช้ซ้ำได้
│   │   │   ├── sidebar.py          # เมนูนำทางด้านซ้าย
│   │   │   ├── topbar.py           # แถบหัวเรื่องด้านบน
│   │   │   └── sources_dialog.py   # Dialog สำหรับจัดการแหล่งข่าว
│   │   ├── pages/                  # หน้าจอต่างๆ ของแอปพลิเคชัน
│   │   │   ├── dashboard.py        # หน้าหลักแสดงการ์ดข่าว
│   │   │   ├── config.py           # หน้าตั้งค่าผู้ใช้
│   │   │   ├── detail.py           # หน้ารายละเอียดข่าว + การแปล
│   │   │   ├── style.py            # หน้าตั้งค่ารูปแบบ AI Output
│   │   │   ├── profiles.py         # หน้าจัดการโปรไฟล์ผู้ใช้
│   │   │   └── about.py            # หน้าข้อมูลเกี่ยวกับแอปพลิเคชัน
│   │   ├── main.py                 # จุดเริ่มต้นและ Page Routing
│   │   └── theme.py                # Color Scheme และ Design Tokens
│   └── utils/                      # Utilities ที่ใช้ร่วมกัน
│       ├── exceptions.py           # Custom Exception Classes
│       ├── logger.py               # การตั้งค่า Logging
│       ├── paths.py                # การจัดการ File Path
│       └── system_check.py         # ตรวจสอบความพร้อมของระบบ
├── data/
│   └── schema.sql                  # Database Schema พร้อม Seed Data
├── run_ui.py                       # จุดเริ่มต้นหลัก (python run_ui.py)
├── build_app.spec                  # การตั้งค่า PyInstaller Build
├── installer.iss                   # Script สำหรับ InnoSetup Installer
└── requirements.txt                # Python Dependencies
```

### 3.2 คำอธิบายแต่ละไดเรกทอรี

#### 3.2.1 `app/` — แพ็กเกจหลัก

นี่คือ Root Package ของแอปพลิเคชัน ประกอบด้วย 4 Sub-packages หลัก:

**`app/config/`** — การตั้งค่า
- `settings.py` — ไฟล์นี้ว่างเปล่าโดยเจตนา เนื่องจากการตั้งค่าทั้งหมดถูกเก็บใน:
  - SQLite Database (ตาราง `system_profile`, `user_profiles`, `styles`)
  - ไม่ใช้ JSON config file แยก

**`app/services/`** — ชั้น Backend Logic

| ไฟล์ | หน้าที่ | คลาส/ฟังก์ชันหลัก |
|-----|--------|------------------|
| `ai_engine.py` | High-level wrapper สำหรับการเรียกใช้ AI | `AIEngine.score_article()`, `AIEngine.translate_article()` |
| `backend_api.py` | Facade Pattern รวมทุก Service เป็นจุดเข้าถึงเดียว | `BackendAPI` singleton instance |
| `database_manager.py` | CRUD Operations สำหรับทุกตารางใน SQLite | `DatabaseManager` class |
| `ollama_engine.py` | HTTP Client สำหรับ Ollama REST API | `OllamaEngine.chat()` |
| `prompt_builder.py` | สร้าง System/User Prompt จาก Style settings | `PromptBuilder.build_scoring_prompt()`, `build_translation_prompt()` |
| `scraper_service.py` | ดึงข่าวจากเว็บไซต์แบบ Async | `ScraperService.fetch_all_sources()` |

**`app/ui/`** — ชั้น Frontend

| ไดเรกทอรี/ไฟล์ | หน้าที่ |
|---------------|--------|
| `components/` | UI Components ที่ใช้ซ้ำในหลายหน้า |
| `pages/` | หน้าจอหลักของแอปพลิเคชัน (แต่ละไฟล์ = 1 หน้า) |
| `main.py` | Entry point, จัดการ routing ระหว่างหน้า |
| `theme.py` | กำหนด Colors, Fonts, Spacing ที่ใช้ทั่วทั้งแอป |

**`app/utils/`** — Utilities

| ไฟล์ | หน้าที่ |
|-----|--------|
| `exceptions.py` | Custom Exceptions เช่น `ScraperError`, `AIEngineError` |
| `logger.py` | ตั้งค่า Python Logging ให้บันทึกลงไฟล์และ Console |
| `paths.py` | ฟังก์ชันหา Path ต่างๆ เช่น Database, Logs, User Data |
| `system_check.py` | ตรวจสอบว่า Ollama ทำงานอยู่หรือไม่, โมเดลพร้อมใช้หรือไม่ |

#### 3.2.2 `data/` — ข้อมูลและ Schema

- `schema.sql` — ไฟล์ SQL ที่ประกอบด้วย:
  - คำสั่ง `CREATE TABLE` สำหรับทุกตาราง
  - คำสั่ง `INSERT` สำหรับ Seed Data เริ่มต้น
  - ถูก Execute ครั้งเดียวตอนสร้าง Database ใหม่

#### 3.2.3 Root Files

| ไฟล์ | หน้าที่ |
|-----|--------|
| `run_ui.py` | Entry point หลัก — รันด้วย `python run_ui.py` |
| `build_app.spec` | Config สำหรับ PyInstaller กำหนดไฟล์ที่ต้อง Bundle |
| `installer.iss` | Script สำหรับ InnoSetup สร้าง Windows Installer |
| `requirements.txt` | รายการ Python packages ที่ต้องติดตั้ง |

---

## 4. การออกแบบฐานข้อมูล (Database Design)

### 4.1 ภาพรวม Entity-Relationship

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  master_status  │       │     models      │       │ system_profile  │
│  (สถานะกลาง)    │       │  (โมเดล AI)     │       │  (Singleton)    │
└────────┬────────┘       └────────┬────────┘       └─────────────────┘
         │                         │                          
         │ status_id               │ active_model_id          
         ▼                         ▼                          
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    sources      │       │  user_profiles  │◄──────│     styles      │
│   (แหล่งข่าว)   │       │  (โปรไฟล์)      │       │  (รูปแบบ AI)    │
└────────┬────────┘       └────────┬────────┘       └────────┬────────┘
         │                         │                          │
         │ source_id               │ profile_id               │ used_style_id
         ▼                         ▼                          ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  articles_meta  │───────│      tags       │       │ article_content │
│  (Metadata)     │       │   (Keywords)    │       │  (เนื้อหาเต็ม)  │
└────────┬────────┘       └────────┬────────┘       └─────────────────┘
         │                         │                          
         │                         │                          
         └─────────────┬───────────┘                          
                       ▼                                      
              ┌─────────────────┐                             
              │ article_tag_map │                             
              │    (M:N Map)    │                             
              └─────────────────┘                             
                                                              
┌─────────────────┐                                           
│      logs       │                                           
│  (บันทึกระบบ)   │                                           
└─────────────────┘                                           
```

### 4.2 รายละเอียดแต่ละตาราง

---

#### 4.2.1 `master_status` — ตารางสถานะกลาง

**วัตถุประสงค์:** เก็บค่าสถานะที่ใช้ร่วมกันทั่วทั้งระบบ เป็น Lookup Table กลาง

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `status_id` | INTEGER | PRIMARY KEY | รหัสสถานะ |
| `status_name` | TEXT | NOT NULL | ชื่อสถานะ เช่น "Active", "Inactive" |
| `status_group` | TEXT | | กลุ่มของสถานะ เช่น "General", "Article", "Model" |
| `description` | TEXT | | คำอธิบายเพิ่มเติม |

**Seed Data:**

```sql
INSERT INTO master_status (status_id, status_name, status_group, description) VALUES
(1, 'Active', 'General', 'Item is active and usable'),
(2, 'Inactive', 'General', 'Item is disabled'),
(3, 'New', 'Article', 'Just scraped, waiting for score'),
(4, 'Scored', 'Article', 'AI has assigned a score'),
(5, 'Translated', 'Article', 'Translation complete'),
(6, 'Online', 'Source', 'Website is reachable'),
(7, 'Offline', 'Source', 'Website is down');
```

---

#### 4.2.2 `models` — ทะเบียนโมเดล AI

**วัตถุประสงค์:** เก็บข้อมูลโมเดล AI ที่ระบบรองรับ

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `model_id` | INTEGER | PRIMARY KEY | รหัสโมเดล |
| `model_name` | TEXT | NOT NULL UNIQUE | ชื่อโมเดล เช่น "typhoon2.5-qwen3-4b" |
| `file_path` | TEXT | | Path ไปยังไฟล์โมเดล (ถ้ามี) |
| `model_type` | TEXT | | ประเภทโมเดล เช่น "LLM", "Embedding" |
| `max_tokens` | INTEGER | DEFAULT 4096 | จำนวน Token สูงสุดที่รองรับ |
| `status_id` | INTEGER | FOREIGN KEY → master_status | สถานะโมเดล (Online/Offline) |

**Seed Data:**

```sql
-- ไม่มี Seed Data สำหรับตารางนี้ — โมเดลจะถูกตรวจจับอัตโนมัติจาก Ollama
```

---

#### 4.2.3 `system_profile` — ค่าคอนฟิกระบบ (Singleton)

**วัตถุประสงค์:** เก็บการตั้งค่าระดับระบบ มีแถวเดียวเท่านั้น (Singleton Pattern)

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `profile_id` | INTEGER | PRIMARY KEY CHECK(profile_id = 1) | ต้องเป็น 1 เสมอ (Singleton) |
| `org_name` | TEXT | | ชื่อองค์กร |
| `threshold_mandatory` | INTEGER | DEFAULT 2 | คะแนนขั้นต่ำสำหรับข่าวที่ต้องแสดง |
| `threshold_max` | INTEGER | DEFAULT 5 | คะแนนสูงสุด |
| `active_model_id` | INTEGER | FOREIGN KEY → models | โมเดล AI ที่ใช้งานอยู่ |
| `model_name` | TEXT | | ชื่อโมเดลที่ใช้งาน (Denormalized) |
| `is_new_news` | INTEGER | DEFAULT 1 | แสดงข่าวใหม่หรือไม่ (0/1) |
| `is_related` | INTEGER | DEFAULT 1 | แสดงเฉพาะข่าวที่เกี่ยวข้องหรือไม่ |
| `auto_scoring_status` | INTEGER | DEFAULT 1 | เปิดการให้คะแนนอัตโนมัติ |
| `auto_translate_status` | INTEGER | DEFAULT 0 | เปิดการแปลอัตโนมัติ |
| `date_limit_days` | INTEGER | DEFAULT 14 | จำนวนวันย้อนหลังสำหรับดึงข่าว (1-30) |
| `threshold` | REAL | DEFAULT 5.0 | Threshold ทั่วไป |

**หมายเหตุสำคัญ:** ตารางนี้มี `CHECK(profile_id = 1)` เพื่อบังคับให้มีแถวเดียวเท่านั้น

---

#### 4.2.4 `user_profiles` — โปรไฟล์ผู้ใช้

**วัตถุประสงค์:** รองรับหลายโปรไฟล์ผู้ใช้ แต่ละโปรไฟล์มี Keywords และ Styles ของตัวเอง

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `profile_id` | INTEGER | PRIMARY KEY | รหัสโปรไฟล์ |
| `profile_name` | TEXT | NOT NULL UNIQUE | ชื่อโปรไฟล์ |
| `description` | TEXT | | คำอธิบายโปรไฟล์ |
| `active_style_id` | INTEGER | FOREIGN KEY → styles | Style ที่ใช้งานอยู่ |
| `is_active` | INTEGER | DEFAULT 0 | เป็นโปรไฟล์ที่เลือกอยู่หรือไม่ |
| `is_system` | INTEGER | DEFAULT 0 | เป็นโปรไฟล์ระบบ (ลบไม่ได้) |

**Seed Data:**

```sql
INSERT INTO user_profiles (profile_id, profile_name, description, is_active, is_system) VALUES
(1, 'Technology & AI', 'ติดตามข่าวเทคโนโลยีและปัญญาประดิษฐ์', 1, 1),
(2, 'Finance & Markets', 'ติดตามข่าวการเงินและตลาดทุน', 0, 0),
(3, 'Politics & Policy', 'ติดตามข่าวการเมืองและนโยบาย', 0, 0);
```

---

#### 4.2.5 `tags` — คีย์เวิร์ดและโดเมน

**วัตถุประสงค์:** เก็บ Keywords และ Domains ที่แต่ละโปรไฟล์สนใจ

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `tag_id` | INTEGER | PRIMARY KEY | รหัส Tag |
| `tag_name` | TEXT | NOT NULL | ชื่อ Tag เช่น "AI", "Machine Learning" |
| `tag_type` | TEXT | CHECK(tag_type IN ('Keyword', 'Domain')) | ประเภท: Keyword หรือ Domain |
| `weight_score` | REAL | DEFAULT 1.0 | น้ำหนักคะแนน (สำคัญมาก = สูง) |
| `status_id` | INTEGER | FOREIGN KEY → master_status | สถานะ Active/Inactive |
| `profile_id` | INTEGER | FOREIGN KEY → user_profiles | โปรไฟล์ที่เป็นเจ้าของ |

**Constraints:**
```sql
UNIQUE(tag_name, tag_type, profile_id)
```

**ตัวอย่าง Seed Data:**

```sql
INSERT INTO tags (tag_name, tag_type, weight_score, status_id, profile_id) VALUES
('Artificial Intelligence', 'Keyword', 2.0, 1, 1),
('Machine Learning', 'Keyword', 1.5, 1, 1),
('Large Language Model', 'Keyword', 2.0, 1, 1),
('Cryptocurrency', 'Keyword', 1.0, 1, 2),
('Stock Market', 'Keyword', 1.5, 1, 2);
```

---

#### 4.2.6 `sources` — แหล่งข่าว

**วัตถุประสงค์:** เก็บรายการเว็บไซต์ข่าวที่ระบบจะดึงบทความมา

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `source_id` | INTEGER | PRIMARY KEY | รหัสแหล่งข่าว |
| `domain_name` | TEXT | NOT NULL | ชื่อโดเมน เช่น "techcrunch.com" |
| `base_url` | TEXT | NOT NULL UNIQUE | URL หลัก เช่น "https://techcrunch.com" |
| `scraper_type` | TEXT | CHECK(scraper_type IN ('RSS', 'HTML')) | วิธีดึงข่าว: RSS Feed หรือ HTML Scraping |
| `status_id` | INTEGER | FOREIGN KEY → master_status | สถานะ Active/Inactive |
| `last_checked_at` | TEXT | | Timestamp ครั้งสุดท้ายที่ตรวจสอบ |

**ตัวอย่าง Seed Data:**

```sql
INSERT INTO sources (domain_name, base_url, scraper_type, status_id) VALUES
('techcrunch.com', 'https://techcrunch.com', 'RSS', 1),
('arstechnica.com', 'https://arstechnica.com', 'RSS', 1),
('reuters.com', 'https://www.reuters.com', 'HTML', 1);
```

---

#### 4.2.7 `styles` — รูปแบบผลลัพธ์ AI

**วัตถุประสงค์:** กำหนดรูปแบบการแปลและการสรุปของ AI

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `style_id` | INTEGER | PRIMARY KEY | รหัส Style |
| `name` | TEXT | NOT NULL UNIQUE | ชื่อ Style |
| `output_type` | TEXT | | ประเภทผลลัพธ์ เช่น "news_article", "social_media" |
| `tone` | TEXT | | โทนการเขียน: "professional", "conversational", "formal" |
| `headline_length` | INTEGER | | ความยาวหัวข้อ (ตัวอักษร) |
| `lead_length` | INTEGER | | ความยาวย่อหน้านำ (ตัวอักษร) |
| `body_length` | INTEGER | | ความยาวเนื้อหา (ตัวอักษร) |
| `analysis_length` | INTEGER | | ความยาวบทวิเคราะห์ (ตัวอักษร) |
| `include_keywords` | INTEGER | DEFAULT 1 | รวม Keywords หรือไม่ |
| `include_lead` | INTEGER | DEFAULT 1 | รวมย่อหน้านำหรือไม่ |
| `include_analysis` | INTEGER | DEFAULT 0 | รวมบทวิเคราะห์หรือไม่ |
| `include_source` | INTEGER | DEFAULT 1 | รวมแหล่งที่มาหรือไม่ |
| `include_hashtags` | INTEGER | DEFAULT 0 | รวม Hashtags หรือไม่ |
| `custom_instructions` | TEXT | | คำสั่งเพิ่มเติมสำหรับ AI |
| `is_active` | INTEGER | DEFAULT 1 | เปิดใช้งานหรือไม่ |
| `is_default` | INTEGER | DEFAULT 0 | เป็น Style เริ่มต้นหรือไม่ |

**Seed Data:**

```sql
INSERT INTO styles (style_id, name, output_type, tone, headline_length, lead_length, body_length, is_default) VALUES
(1, 'News Article', 'news_article', 'professional', 100, 200, 500, 1),
(2, 'Social Media', 'social_media', 'conversational', 50, 100, 280, 0),
(3, 'Executive Brief', 'executive_brief', 'formal', 80, 150, 300, 0);
```

---

#### 4.2.8 `articles_meta` — Metadata ข่าว

**วัตถุประสงค์:** เก็บข้อมูลหลักของบทความข่าว

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `article_id` | INTEGER | PRIMARY KEY | รหัสบทความ |
| `source_id` | INTEGER | FOREIGN KEY → sources | แหล่งข่าวที่มาของบทความ |
| `url_hash` | TEXT | NOT NULL UNIQUE | Hash ของ URL (ป้องกัน Duplicate) |
| `published_at` | TEXT | | วันที่เผยแพร่ (ISO 8601) |
| `headline` | TEXT | | หัวข้อข่าว |
| `ai_score` | REAL | | คะแนนความเกี่ยวข้อง (1-10) |
| `status_id` | INTEGER | FOREIGN KEY → master_status | สถานะบทความ (New/Scored/Translated) |
| `article_url` | TEXT | | URL เต็มของบทความ |
| `author_name` | TEXT | | ชื่อผู้เขียน |
| `created_at` | TEXT | DEFAULT CURRENT_TIMESTAMP | วันที่สร้างใน Database |

**กฎสำคัญ:**
> ⚠️ **CRITICAL:** เมื่อ Query ข้อมูล ต้องใช้ `COALESCE(published_at, created_at)` เสมอ เพราะ `published_at` อาจเป็น NULL ถ้าดึงวันที่เผยแพร่ไม่ได้

---

#### 4.2.9 `article_content` — เนื้อหาเต็ม + คำแปล

**วัตถุประสงค์:** เก็บเนื้อหาเต็มและผลการแปล แยกจาก Metadata เพื่อประสิทธิภาพ

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `article_id` | INTEGER | PRIMARY KEY, FOREIGN KEY → articles_meta | รหัสบทความ (1:1) |
| `original_content` | TEXT | | เนื้อหาต้นฉบับ (ภาษาอังกฤษ) |
| `thai_content` | TEXT | | เนื้อหาที่แปลเป็นภาษาไทย |
| `ai_reasoning` | TEXT | | เหตุผลที่ AI ให้คะแนน |
| `used_style_id` | INTEGER | FOREIGN KEY → styles | Style ที่ใช้ในการแปล |

**Constraints:**
```sql
FOREIGN KEY (article_id) REFERENCES articles_meta(article_id) ON DELETE CASCADE
```

**ความสัมพันธ์:** มีความสัมพันธ์แบบ 1:1 กับ `articles_meta` — เมื่อลบ articles_meta จะลบ article_content ตามไปด้วย (CASCADE)

---

#### 4.2.10 `article_tag_map` — ความสัมพันธ์ข่าว-คีย์เวิร์ด

**วัตถุประสงค์:** Mapping Table สำหรับความสัมพันธ์ Many-to-Many ระหว่างบทความและ Tags

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `map_id` | INTEGER | PRIMARY KEY | รหัส Mapping |
| `article_id` | INTEGER | FOREIGN KEY → articles_meta | รหัสบทความ |
| `tag_id` | INTEGER | FOREIGN KEY → tags | รหัส Tag |
| `match_confidence` | REAL | DEFAULT 0.0 | ความมั่นใจในการ Match (0.0-1.0) |

**Constraints:**
```sql
UNIQUE(article_id, tag_id)
```

**ตัวอย่างการใช้งาน:**
```sql
-- หา Tags ทั้งหมดของบทความ
SELECT t.tag_name, atm.match_confidence
FROM article_tag_map atm
JOIN tags t ON atm.tag_id = t.tag_id
WHERE atm.article_id = ?;

-- หาบทความทั้งหมดที่มี Tag "AI"
SELECT am.headline, am.ai_score
FROM articles_meta am
JOIN article_tag_map atm ON am.article_id = atm.article_id
JOIN tags t ON atm.tag_id = t.tag_id
WHERE t.tag_name = 'AI';
```

---

#### 4.2.11 `logs` — บันทึกระบบ

**วัตถุประสงค์:** เก็บ Log การทำงานของระบบสำหรับ Debug และ Audit

| คอลัมน์ | ชนิดข้อมูล | Constraints | คำอธิบาย |
|--------|-----------|-------------|----------|
| `log_id` | INTEGER | PRIMARY KEY | รหัส Log |
| `log_level` | TEXT | | ระดับ Log: DEBUG, INFO, WARNING, ERROR |
| `component` | TEXT | | ส่วนประกอบที่สร้าง Log เช่น "Scraper", "AIEngine" |
| `message` | TEXT | | ข้อความ Log |
| `created_at` | TEXT | DEFAULT CURRENT_TIMESTAMP | เวลาที่สร้าง |

### 4.3 แผนภาพความสัมพันธ์ (ERD Summary)

```
                                    ┌─────────────────┐
                                    │  master_status  │
                                    │  (Lookup Table) │
                                    └────────┬────────┘
                                             │
              ┌──────────────────────────────┼──────────────────────────────┐
              │                              │                              │
              ▼                              ▼                              ▼
     ┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
     │     sources     │           │      tags       │           │     models      │
     │   (แหล่งข่าว)   │           │   (Keywords)    │           │   (AI Models)   │
     └────────┬────────┘           └────────┬────────┘           └────────┬────────┘
              │                              │                              │
              │ source_id                    │ profile_id                   │ active_model_id
              │                              │                              │
              ▼                              ▼                              ▼
     ┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
     │  articles_meta  │◄─────────►│  user_profiles  │◄─────────►│ system_profile  │
     │   (Metadata)    │           │  (โปรไฟล์)      │           │  (Singleton)    │
     └────────┬────────┘           └────────┬────────┘           └─────────────────┘
              │                              │
              │ article_id (1:1)             │ active_style_id
              │                              │
              ▼                              ▼
     ┌─────────────────┐           ┌─────────────────┐
     │ article_content │           │     styles      │
     │  (เนื้อหาเต็ม)  │           │  (รูปแบบ AI)    │
     └────────┬────────┘           └─────────────────┘
              │
              │ article_id (M:N via article_tag_map)
              │
              ▼
     ┌─────────────────┐
     │ article_tag_map │
     │    (M:N Map)    │
     └─────────────────┘
```

---

## 5. การออกแบบส่วนประกอบ (Component Design)

### 5.1 ScraperService (`scraper_service.py`)

#### 5.1.1 ภาพรวม

`ScraperService` เป็นหัวใจของระบบดึงข่าว รับผิดชอบการค้นหาและดึงบทความจากเว็บไซต์ข่าวต่างๆ

#### 5.1.2 Waterfall Discovery Strategy

การค้นหา Feed/Content ใช้กลยุทธ์ Waterfall — ลองทีละวิธี หากล้มเหลวให้ลองวิธีถัดไป:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Waterfall Discovery Flow                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ขั้นตอน 1: ลอง RSS Feed Paths มาตรฐาน                             │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  /feed, /rss, /feed.xml, /rss.xml, /atom.xml                │   │
│   │  /feeds/posts/default, /feed/atom                           │   │
│   └──────────────────────────┬──────────────────────────────────┘   │
│                              │                                       │
│                    พบ RSS?   ▼   ไม่พบ                              │
│                      ┌───────┴───────┐                              │
│                      │               │                              │
│                      ▼               ▼                              │
│                 ใช้ RSS Feed    ขั้นตอน 2: ลอง Sitemap XML          │
│                              ┌─────────────────────────────────┐    │
│                              │  /sitemap.xml, /sitemap_index.xml│   │
│                              │  /news-sitemap.xml               │   │
│                              └──────────────┬──────────────────┘    │
│                                             │                        │
│                                   พบ Sitemap? ▼  ไม่พบ              │
│                                      ┌───────┴───────┐              │
│                                      │               │              │
│                                      ▼               ▼              │
│                                 ใช้ Sitemap     ขั้นตอน 3: HTML     │
│                                           ┌─────────────────────┐   │
│                                           │  ดึง Links จาก      │   │
│                                           │  Homepage โดยตรง    │   │
│                                           └─────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 5.1.3 Content Extraction Pipeline

การดึงเนื้อหาจาก HTML ใช้ 2 Library โดย trafilatura เป็นตัวหลัก:

```python
def extract_content(html: str, url: str) -> dict:
    """
    ดึงเนื้อหาจาก HTML โดยใช้ trafilatura เป็นหลัก
    fallback ไปยัง newspaper3k ถ้าล้มเหลว
    """
    # ลอง trafilatura ก่อน
    content = trafilatura.extract(html, include_comments=False)
    if content and len(content) > 200:
        return {"content": content, "extractor": "trafilatura"}
    
    # Fallback: newspaper3k
    article = Article(url)
    article.set_html(html)
    article.parse()
    if article.text and len(article.text) > 200:
        return {"content": article.text, "extractor": "newspaper3k"}
    
    return None  # ดึงเนื้อหาไม่สำเร็จ
```

#### 5.1.4 Filtering Pipeline

ก่อนบันทึกบทความ ต้องผ่านตัวกรองหลายขั้นตอน:

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Article Filtering Pipeline                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Raw Article                                                          │
│       │                                                               │
│       ▼                                                               │
│  ┌─────────────────┐                                                  │
│  │ 1. Date Filter  │  ตรวจสอบว่าอยู่ในช่วง date_limit_days หรือไม่   │
│  └────────┬────────┘                                                  │
│           │ ผ่าน                                                      │
│           ▼                                                           │
│  ┌─────────────────┐                                                  │
│  │ 2. Domain Check │  ตรวจสอบว่ามาจากแหล่งข่าวที่ Active หรือไม่      │
│  └────────┬────────┘                                                  │
│           │ ผ่าน                                                      │
│           ▼                                                           │
│  ┌─────────────────┐                                                  │
│  │ 3. Duplicate    │  ตรวจสอบ url_hash ว่าซ้ำใน Database หรือไม่      │
│  │    Check        │                                                  │
│  └────────┬────────┘                                                  │
│           │ ผ่าน                                                      │
│           ▼                                                           │
│  ┌─────────────────┐                                                  │
│  │ 4. Paywall      │  ตรวจหาสัญญาณ Paywall เช่น "Subscribe to read"   │
│  │    Detection    │                                                  │
│  └────────┬────────┘                                                  │
│           │ ผ่าน                                                      │
│           ▼                                                           │
│  ┌─────────────────┐                                                  │
│  │ 5. Content      │  ตรวจสอบว่าเนื้อหายาวพอ (> 200 ตัวอักษร)         │
│  │    Length       │                                                  │
│  └────────┬────────┘                                                  │
│           │ ผ่าน                                                      │
│           ▼                                                           │
│  ┌─────────────────┐                                                  │
│  │ 6. Keyword      │  ตรวจสอบว่ามี Keywords ที่ผู้ใช้สนใจหรือไม่       │
│  │    Matching     │  (Optional - ขึ้นกับการตั้งค่า)                   │
│  └────────┬────────┘                                                  │
│           │ ผ่าน                                                      │
│           ▼                                                           │
│       Accepted                                                        │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

#### 5.1.5 Async Batch Processing

การดึงข่าวใช้ `asyncio.gather()` เพื่อประสิทธิภาพ:

```python
async def fetch_all_sources(self, sources: list, batch_size: int = 5) -> list:
    """
    ดึงข่าวจากหลาย Source พร้อมกันแบบ Batch
    
    Args:
        sources: รายการแหล่งข่าว
        batch_size: จำนวน Source ที่ดึงพร้อมกัน (default: 5)
    
    Returns:
        รายการบทความที่ดึงได้
    """
    all_articles = []
    
    # แบ่งเป็น Batch
    for i in range(0, len(sources), batch_size):
        batch = sources[i:i + batch_size]
        
        # ดึงทุก Source ใน Batch พร้อมกัน
        tasks = [self.fetch_source(source) for source in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
    
    return all_articles
```

---

### 5.2 AI Engine (`ai_engine.py` + `ollama_engine.py`)

#### 5.2.1 สถาปัตยกรรม

```
┌─────────────────────────────────────────────────────────────────┐
│                       AI Engine Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │
│  │   AIEngine   │─────►│ OllamaEngine │─────►│   Ollama     │   │
│  │  (High-level)│      │ (HTTP Client)│      │   Server     │   │
│  └──────────────┘      └──────────────┘      │  :11434      │   │
│         │                                     └──────────────┘   │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │PromptBuilder │                                               │
│  │ (สร้าง Prompt)│                                               │
│  └──────────────┘                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.2.2 การเชื่อมต่อ Ollama

**Endpoint:** `http://localhost:11434/api/chat`

**Model:** `scb10x/typhoon2.5-qwen3-4b:latest`

> ⚠️ **กฎสำคัญที่สุด:** ห้ามใช้ `/api/generate` โดยเด็ดขาด — ต้องใช้ `/api/chat` เท่านั้น
>
> เหตุผล: Typhoon 2.5 ถูกออกแบบมาสำหรับ Chat API และให้ผลลัพธ์ที่ดีกว่ามากเมื่อใช้กับ Chat format

**ตัวอย่าง Request:**

```python
async def chat(self, messages: list[dict], model: str = None) -> str:
    """
    ส่งข้อความไปยัง Ollama Chat API
    
    Args:
        messages: รายการข้อความในรูปแบบ [{"role": "system/user", "content": "..."}]
        model: ชื่อโมเดล (default: typhoon2.5-qwen3-4b)
    
    Returns:
        ข้อความตอบกลับจาก AI
    """
    model = model or "scb10x/typhoon2.5-qwen3-4b:latest"
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/chat",  # ต้องเป็น /api/chat เสมอ!
            json=payload
        ) as response:
            result = await response.json()
            return result["message"]["content"]
```

#### 5.2.3 Scoring Function

```python
async def score_article(self, article: dict, keywords: list[str]) -> dict:
    """
    ให้คะแนนความเกี่ยวข้องของบทความกับ Keywords
    
    Returns:
        {
            "score": int (1-10),
            "reasoning": str,
            "matched_keywords": list[str]
        }
    """
    prompt = self.prompt_builder.build_scoring_prompt(
        headline=article["headline"],
        content=article["content"],
        keywords=keywords
    )
    
    response = await self.ollama.chat(prompt)
    
    # Parse response เพื่อดึง score (integer 1-10)
    score = self._parse_score(response)
    
    return {
        "score": score,
        "reasoning": response,
        "matched_keywords": self._extract_matched_keywords(response, keywords)
    }
```

#### 5.2.4 Translation Function

```python
async def translate_article(self, article: dict, style_id: int) -> str:
    """
    แปลบทความเป็นภาษาไทยตาม Style ที่กำหนด
    
    Args:
        article: ข้อมูลบทความ
        style_id: รหัส Style ที่ใช้
    
    Returns:
        เนื้อหาที่แปลแล้ว
    """
    style = self.db.get_style(style_id)
    
    prompt = self.prompt_builder.build_translation_prompt(
        content=article["content"],
        style=style
    )
    
    response = await self.ollama.chat(prompt)
    return response
```

---

### 5.3 Prompt Builder (`prompt_builder.py`)

#### 5.3.1 หลักการออกแบบ

**กฎสำคัญ:** ห้าม Hardcode คำสั่งใดๆ ใน Prompt — ทุกอย่างต้องมาจาก Style settings ใน Database

```
┌─────────────────────────────────────────────────────────────────┐
│                    Prompt Construction Flow                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │
│  │    Style     │─────►│PromptBuilder │─────►│   Messages   │   │
│  │  (from DB)   │      │  .build()    │      │  for Ollama  │   │
│  └──────────────┘      └──────────────┘      └──────────────┘   │
│                                                                  │
│  Style Settings:                                                 │
│  - tone: "professional" / "conversational" / "formal"           │
│  - output_type: "news_article" / "social_media" / "brief"       │
│  - headline_length: 100                                          │
│  - body_length: 500                                              │
│  - include_analysis: true/false                                  │
│  - custom_instructions: "เน้นข้อมูลทางเทคนิค..."                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.3.2 Tone Mapping

| Tone ใน Database | การเขียนภาษาไทย |
|-----------------|----------------|
| `professional` | ใช้ภาษาทางการ หลีกเลี่ยงคำแสลง เหมาะสำหรับรายงานข่าว |
| `conversational` | ใช้ภาษาเป็นกันเอง อ่านง่าย เหมาะสำหรับ Social Media |
| `formal` | ใช้ภาษาราชการ เหมาะสำหรับรายงานผู้บริหาร |

#### 5.3.3 ตัวอย่างการสร้าง Prompt

```python
def build_translation_prompt(self, content: str, style: dict) -> list[dict]:
    """
    สร้าง Prompt สำหรับการแปลภาษา
    """
    # สร้าง System Message จาก Style
    system_parts = [
        f"คุณเป็นนักแปลข่าวมืออาชีพ ใช้โทน{self._tone_to_thai(style['tone'])}",
        f"ความยาวหัวข้อ: ไม่เกิน {style['headline_length']} ตัวอักษร",
        f"ความยาวเนื้อหา: ประมาณ {style['body_length']} ตัวอักษร",
    ]
    
    if style.get('include_analysis'):
        system_parts.append(f"รวมบทวิเคราะห์: ความยาวประมาณ {style['analysis_length']} ตัวอักษร")
    
    if style.get('include_hashtags'):
        system_parts.append("รวม Hashtags ที่เกี่ยวข้อง 3-5 รายการ")
    
    if style.get('custom_instructions'):
        system_parts.append(f"คำสั่งเพิ่มเติม: {style['custom_instructions']}")
    
    system_message = "\n".join(system_parts)
    
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"แปลบทความนี้เป็นภาษาไทย:\n\n{content}"}
    ]

def _tone_to_thai(self, tone: str) -> str:
    """แปลง Tone เป็นคำอธิบายภาษาไทย"""
    mapping = {
        "professional": "เป็นทางการ",
        "conversational": "เป็นกันเอง",
        "formal": "ทางราชการ"
    }
    return mapping.get(tone, "เป็นกลาง")
```

---

### 5.4 Database Manager (`database_manager.py`)

#### 5.4.1 หน้าที่หลัก

`DatabaseManager` เป็น Class ที่รวม CRUD Operations ทั้งหมดสำหรับ 11 ตารางใน SQLite

#### 5.4.2 Profile-Aware Queries

**กฎสำคัญ:** หลายฟังก์ชันต้องกรองตาม `profile_id` ของโปรไฟล์ที่ Active อยู่

```python
def get_keywords(self, profile_id: int = None) -> list[dict]:
    """
    ดึง Keywords ของโปรไฟล์ที่ระบุ
    ถ้าไม่ระบุ จะใช้โปรไฟล์ที่ Active อยู่
    """
    if profile_id is None:
        profile_id = self.get_active_profile_id()
    
    query = """
        SELECT tag_id, tag_name, tag_type, weight_score
        FROM tags
        WHERE profile_id = ? AND status_id = 1
        ORDER BY weight_score DESC
    """
    return self.execute_query(query, (profile_id,))

def get_active_profile_id(self) -> int:
    """ดึง profile_id ของโปรไฟล์ที่เลือกอยู่"""
    query = "SELECT profile_id FROM user_profiles WHERE is_active = 1 LIMIT 1"
    result = self.execute_query(query)
    return result[0]["profile_id"] if result else 1  # Default to profile 1
```

#### 5.4.3 การจัดการวันที่

> ⚠️ **กฎสำคัญที่สุด:** ห้ามใช้ `published_at` โดยตรง — ต้องใช้ `COALESCE(published_at, created_at)` เสมอ

```python
def get_recent_articles(self, days: int = 7) -> list[dict]:
    """
    ดึงบทความล่าสุดตามจำนวนวันที่กำหนด
    """
    query = """
        SELECT 
            am.article_id,
            am.headline,
            am.ai_score,
            COALESCE(am.published_at, am.created_at) as effective_date,
            ac.thai_content
        FROM articles_meta am
        LEFT JOIN article_content ac ON am.article_id = ac.article_id
        WHERE date(COALESCE(am.published_at, am.created_at)) >= date('now', ?)
        ORDER BY effective_date DESC
    """
    return self.execute_query(query, (f"-{days} days",))
```

#### 5.4.4 Pattern: Insert or Update

```python
def upsert_article(self, article: dict) -> int:
    """
    Insert บทความใหม่ หรือ Update ถ้ามีอยู่แล้ว (based on url_hash)
    
    Returns:
        article_id ของบทความ
    """
    # ตรวจสอบว่ามีอยู่แล้วหรือไม่
    existing = self.get_article_by_url_hash(article["url_hash"])
    
    if existing:
        # Update
        query = """
            UPDATE articles_meta 
            SET headline = ?, ai_score = ?, status_id = ?
            WHERE article_id = ?
        """
        self.execute_query(query, (
            article["headline"],
            article.get("ai_score"),
            article.get("status_id", 3),  # Default: New
            existing["article_id"]
        ))
        return existing["article_id"]
    else:
        # Insert
        query = """
            INSERT INTO articles_meta 
            (source_id, url_hash, published_at, headline, article_url, status_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor = self.execute_query(query, (
            article["source_id"],
            article["url_hash"],
            article.get("published_at"),
            article["headline"],
            article["article_url"],
            3  # New
        ))
        return cursor.lastrowid
```

---

### 5.5 UI Layer (`ui/`)

#### 5.5.1 สถาปัตยกรรม

```
┌─────────────────────────────────────────────────────────────────┐
│                       Flet UI Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        main.py                            │   │
│  │  - App Entry Point                                        │   │
│  │  - Page Routing (page.route)                              │   │
│  │  - Theme Configuration                                    │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│         ┌─────────────────────┼─────────────────────┐           │
│         │                     │                     │           │
│         ▼                     ▼                     ▼           │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐     │
│  │   sidebar   │      │   topbar    │      │   pages/    │     │
│  │   (Nav)     │      │  (Header)   │      │  (Content)  │     │
│  └─────────────┘      └─────────────┘      └──────┬──────┘     │
│                                                    │            │
│         ┌─────────────────────────────────────────┤            │
│         │           │           │           │     │            │
│         ▼           ▼           ▼           ▼     ▼            │
│   ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐│
│   │dashboard ││  config  ││  detail  ││  style   ││ profiles ││
│   └──────────┘└──────────┘└──────────┘└──────────┘└──────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.5.2 Page Routing

```python
# main.py
def main(page: ft.Page):
    page.title = "AIEAT News Dashboard"
    page.theme = theme.get_theme()
    
    def route_change(e):
        page.views.clear()
        
        if page.route == "/" or page.route == "/dashboard":
            page.views.append(dashboard.DashboardPage(page))
        elif page.route == "/config":
            page.views.append(config.ConfigPage(page))
        elif page.route == "/detail":
            page.views.append(detail.DetailPage(page))
        elif page.route == "/style":
            page.views.append(style.StylePage(page))
        elif page.route == "/profiles":
            page.views.append(profiles.ProfilesPage(page))
        elif page.route == "/about":
            page.views.append(about.AboutPage(page))
        
        page.update()
    
    page.on_route_change = route_change
    page.go("/dashboard")

ft.app(target=main)
```

#### 5.5.3 Async Operations

> ⚠️ **กฎสำคัญที่สุดสำหรับ UI:** ห้ามใช้ `threading.Thread` + `page.update()` โดยตรง — ต้องใช้ `page.run_task()` เสมอ

**ผิด:**
```python
# ❌ ห้ามทำแบบนี้!
def on_fetch_click(e):
    def fetch_in_thread():
        articles = scraper.fetch_all()  # Blocking call
        update_ui(articles)
        page.update()  # อาจ crash หรือไม่ update
    
    threading.Thread(target=fetch_in_thread).start()
```

**ถูก:**
```python
# ✅ ใช้ page.run_task() เสมอ
async def on_fetch_click(e):
    async def fetch_articles():
        loading_indicator.visible = True
        page.update()
        
        try:
            articles = await scraper.fetch_all_sources(sources)
            update_article_list(articles)
        finally:
            loading_indicator.visible = False
            page.update()
    
    await page.run_task(fetch_articles)
```

#### 5.5.4 Component Pattern

แต่ละ Component เป็น Function ที่ Return Flet Control:

```python
# components/sidebar.py
def Sidebar(page: ft.Page, active_route: str) -> ft.Container:
    """
    สร้าง Navigation Sidebar
    
    Args:
        page: Flet Page object
        active_route: Route ที่เลือกอยู่ปัจจุบัน
    
    Returns:
        Container ที่ประกอบด้วยเมนูนำทาง
    """
    def nav_item(icon, label, route):
        is_active = active_route == route
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=ft.colors.PRIMARY if is_active else ft.colors.ON_SURFACE),
                ft.Text(label, weight=ft.FontWeight.BOLD if is_active else None)
            ]),
            bgcolor=ft.colors.PRIMARY_CONTAINER if is_active else None,
            padding=10,
            border_radius=8,
            on_click=lambda _: page.go(route)
        )
    
    return ft.Container(
        content=ft.Column([
            nav_item(ft.icons.DASHBOARD, "Dashboard", "/dashboard"),
            nav_item(ft.icons.SETTINGS, "Settings", "/config"),
            nav_item(ft.icons.STYLE, "AI Style", "/style"),
            nav_item(ft.icons.PERSON, "Profiles", "/profiles"),
            nav_item(ft.icons.INFO, "About", "/about"),
        ], spacing=5),
        width=200,
        padding=10,
        bgcolor=ft.colors.SURFACE_VARIANT
    )
```

---

## 6. การติดตั้งและ Deployment

### 6.1 Development Setup

#### 6.1.1 ข้อกำหนดเบื้องต้น

| รายการ | เวอร์ชันขั้นต่ำ | คำอธิบาย |
|--------|---------------|----------|
| Python | 3.10+ | ภาษาหลัก |
| pip | ล่าสุด | Python Package Manager |
| Ollama | ล่าสุด | AI Runtime |
| RAM | 8 GB+ | สำหรับรัน Typhoon 2.5 |
| Disk | 10 GB+ | สำหรับเก็บ Model |

#### 6.1.2 ขั้นตอนการติดตั้ง

```powershell
# 1. Clone Repository
git clone <repository-url>
cd AIEAT_Internship

# 2. สร้าง Virtual Environment (แนะนำ)
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# หรือ
source venv/bin/activate      # macOS/Linux

# 3. ติดตั้ง Dependencies
pip install -r requirements.txt

# 4. ติดตั้งและเริ่ม Ollama (ในหน้าต่าง Terminal แยก)
# ดาวน์โหลดจาก https://ollama.com และติดตั้ง
ollama serve

# 5. ดึง Typhoon 2.5 Model (ครั้งแรกเท่านั้น ~2.5GB)
ollama pull scb10x/typhoon2.5-qwen3-4b:latest

# 6. รันแอปพลิเคชัน
python run_ui.py
```

#### 6.1.3 ตรวจสอบการติดตั้ง

```powershell
# ตรวจสอบว่า Ollama ทำงานอยู่
curl http://localhost:11434/api/tags
# ควรแสดงรายการ Model ที่ติดตั้ง

# ตรวจสอบว่า Typhoon 2.5 พร้อมใช้
ollama list
# ควรเห็น scb10x/typhoon2.5-qwen3-4b:latest ในรายการ
```

### 6.2 Production Build

#### 6.2.1 การสร้าง Standalone Executable

```powershell
# ติดตั้ง PyInstaller (ถ้ายังไม่มี)
pip install pyinstaller

# สร้าง Executable
python -m PyInstaller build_app.spec --clean

# ผลลัพธ์อยู่ที่
# dist/AIEAT/AIEAT.exe
```

#### 6.2.2 โครงสร้าง `build_app.spec`

```python
# build_app.spec
a = Analysis(
    ['run_ui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/schema.sql', 'data'),
        ('app', 'app'),
    ],
    hiddenimports=[
        'flet',
        'aiohttp',
        'trafilatura',
        'newspaper',
    ],
    ...
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='AIEAT',
    icon='assets/icon.ico',  # ถ้ามี
    ...
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name='AIEAT',
)
```

### 6.3 Installer Creation

#### 6.3.1 การสร้าง Windows Installer

```powershell
# ต้องติดตั้ง InnoSetup ก่อน
# ดาวน์โหลดจาก https://jrsoftware.org/isinfo.php

# สร้าง Installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

# ผลลัพธ์
# installer_output/AIEAT_Setup.exe (ประมาณ 71.9 MB)
```

#### 6.3.2 โครงสร้าง `installer.iss`

```iss
; installer.iss
[Setup]
AppName=AIEAT News Dashboard
AppVersion=1.0.0
DefaultDirName={autopf}\AIEAT
DefaultGroupName=AIEAT
OutputDir=installer_output
OutputBaseFilename=AIEAT_Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\AIEAT\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\AIEAT"; Filename: "{app}\AIEAT.exe"
Name: "{commondesktop}\AIEAT"; Filename: "{app}\AIEAT.exe"

[Run]
Filename: "{app}\AIEAT.exe"; Description: "Launch AIEAT"; Flags: postinstall nowait

[Tasks]
Name: "installollama"; Description: "Install Ollama AI Engine"; GroupDescription: "Additional Components:"
```

### 6.4 Ollama Installation Options

#### 6.4.1 ผ่าน Installer Checkbox

เมื่อติดตั้ง AIEAT_Setup.exe ผู้ใช้สามารถเลือก Checkbox "Install Ollama AI Engine" ซึ่งจะ:
1. ดาวน์โหลด Ollama Installer
2. รัน Ollama Setup แบบ Silent
3. ดึง Typhoon 2.5 Model อัตโนมัติ

#### 6.4.2 Manual Installation

```powershell
# รันไฟล์ Install_AI_Engine.bat ที่มากับโปรเจกต์
.\Install_AI_Engine.bat

# หรือติดตั้งเองด้วยคำสั่ง
# 1. ดาวน์โหลดจาก https://ollama.com
# 2. รัน Installer
# 3. เปิด Terminal และรัน:
ollama serve
ollama pull scb10x/typhoon2.5-qwen3-4b:latest
```

---

## 7. ข้อจำกัดและแนวทางพัฒนาต่อ (Limitations & Future Work)

### 7.1 ข้อจำกัดปัจจุบัน

| ข้อจำกัด | รายละเอียด | ผลกระทบ |
|---------|------------|---------|
| **Sequential Fetching** | การดึงบทความจากแต่ละ Source ทำแบบ Sequential ภายใน Source เดียวกัน | ความเร็วในการดึงข่าวอาจช้าถ้ามีบทความมาก |
| **ไม่มี Cloud API** | รองรับเฉพาะ Ollama (Local) ไม่รองรับ OpenAI/Anthropic API | ผู้ใช้ที่ต้องการความเร็วสูงไม่สามารถใช้ Cloud ได้ |
| **ไม่มี Code-Signing** | ไม่ได้ Sign Executable ด้วย Certificate | Windows SmartScreen จะแสดง Warning เมื่อรัน |
| **Single Machine** | ทำงานได้บนเครื่องเดียว ไม่รองรับ Multi-user | ไม่เหมาะสำหรับการ Deploy แบบ Web Application |
| **Hardware Dependent** | ความเร็ว AI ขึ้นกับ CPU/GPU ของเครื่อง | เครื่องที่มี Spec ต่ำอาจประมวลผลช้า |
| **ไม่รองรับ GPU** | Ollama ทำงานบน CPU เป็นค่าเริ่มต้น | ไม่ได้ประโยชน์จาก GPU Acceleration |

### 7.2 แนวทางพัฒนาต่อ

#### 7.2.1 ระยะสั้น (1-3 เดือน)

| Feature | รายละเอียด | ความซับซ้อน |
|---------|------------|-------------|
| **Parallel Article Fetching** | ใช้ `asyncio.gather()` สำหรับบทความหลายรายการภายใน Source เดียวกัน | ต่ำ |
| **GPU Acceleration** | เพิ่มตัวเลือกใช้ Ollama กับ CUDA/ROCm | กลาง |
| **Batch Translation** | แปลหลายบทความพร้อมกันในคำสั่งเดียว | ต่ำ |
| **Export Functions** | Export ข่าวเป็น PDF, CSV, หรือ Markdown | ต่ำ |

#### 7.2.2 ระยะกลาง (3-6 เดือน)

| Feature | รายละเอียด | ความซับซ้อน |
|---------|------------|-------------|
| **Cloud API Option** | เพิ่มตัวเลือก OpenAI/Anthropic สำหรับผู้ใช้ที่ต้องการความเร็ว | กลาง |
| **Code Signing** | ลงทะเบียน Certificate เพื่อลด SmartScreen Warning | กลาง (ต้องซื้อ Certificate) |
| **Scheduled Fetching** | ดึงข่าวอัตโนมัติตามเวลาที่กำหนด (Background Task) | กลาง |
| **Multi-language Support** | รองรับการแปลเป็นภาษาอื่นนอกจากไทย | กลาง |

#### 7.2.3 ระยะยาว (6-12 เดือน)

| Feature | รายละเอียด | ความซับซ้อน |
|---------|------------|-------------|
| **Web Version** | พัฒนาเวอร์ชัน Web สำหรับ Multi-user | สูง |
| **Team Collaboration** | แชร์ Profiles และ Keywords ระหว่างทีม | สูง |
| **Custom Model Training** | Fine-tune โมเดลตามข้อมูลขององค์กร | สูง |
| **Analytics Dashboard** | แสดงสถิติและ Trends ของข่าว | กลาง |

### 7.3 Known Issues

| Issue | สถานะ | Workaround |
|-------|-------|------------|
| Ollama ไม่เริ่มอัตโนมัติ | Open | รัน `ollama serve` ก่อนเปิดแอป |
| บางเว็บไซต์บล็อก Scraper | Open | ใช้ RSS Feed แทน HTML Scraping |
| Memory Leak หลังใช้งานนาน | Investigating | Restart แอปเป็นระยะ |

---

## ภาคผนวก

### ก. รายการ Dependencies (`requirements.txt`)

```
flet
requests
aiohttp
feedparser
beautifulsoup4
certifi
trafilatura
newspaper3k
lxml
justext
courlan
htmldate
python-dateutil
Pillow
```

### ข. คำสั่ง SQL สำหรับสร้างฐานข้อมูล

ดูไฟล์ `data/schema.sql` สำหรับ Schema เต็ม พร้อม Seed Data

### ค. Environment Variables (ถ้ามี)

ระบบนี้ไม่ใช้ Environment Variables — ทุกการตั้งค่าอยู่ใน SQLite Database

---

**สิ้นสุดเอกสาร**

*เวอร์ชัน 1.0 — 23 มีนาคม 2569*
