# Skills Translation Map

## Purpose

`career.md` is the single source of facts about what Aditya has actually done. This file is the concept layer on top of it. Its job is to let resume generation surface relevance to adjacent technologies **without adding tools to the output that Aditya hasn't used**.

## How to use this file

1. When reading a JD, note the tools/keywords it asks for.
2. If a JD tool appears in the "Tool -> Concepts" map below, it's something Aditya has used - frame bullets normally (can name the tool directly).
3. If a JD tool appears only in the "Adjacent Tool -> Concept" map, Aditya has NOT used it. Find the bridging concepts and lead relevant bullets with those concepts. **Do not put the adjacent tool anywhere in the rendered resume, cover letter, or skills section.**
4. The "Concept -> Bullets Index" is the reverse lookup: given a concept keyword from the JD, find which career.md lines demonstrate it.

## Hard rules

- Every concept attributed to a tool below must trace back to a specific line in `career.md`. If there's no line citation, the concept doesn't belong here.
- Adjacent tools are for JD keyword matching and phrasing decisions only. They NEVER appear in rendered output.
- "Planned / not built" work (e.g. RAG pipeline in JobDetective) is concept-level familiarity, not production experience. Frame accordingly - never imply the thing shipped.
- Scope flags matter: "academic project only" or "capstone" is not the same as "4 years in production". Keep the flag when reframing.

---

## 1. Tool -> Concepts Map

### SAP BW on HANA / S4HANA / ABAP / HANA SQL / HANA Calculation Views / SAP BEx / SAP Process Chains (Accenture, Aug 2019 - Jan 2024)
- **Concepts exercised:** enterprise ETL pipeline development and maintenance; month-end data orchestration across financial workstreams (CapEx, OpEx, Revenue, Asset, HR, GL, KPI); real-time and batch data integration; data warehouse monitoring; query optimisation via targeted filters in ABAP / HANA SQL; calculation view design (Graphical and Scripted); self-service reporting enablement; data masking for regulatory compliance (GDPR); release management for data pipelines; root cause analysis in production data systems.
- **Evidence in career.md:** L30 (summary), L52, L54, L55, L56, L57, L62, L63, L64, L65, L66, L69.
- **Scope:** 4+ years, enterprise banking client, production.
- **Adjacent tools (JD keyword matching only - never rendered):** PowerBI, Tableau (Tableau is actually *used* - see Tableau entry below), Looker, Qlik, dbt, Airflow, Snowflake, BigQuery, Redshift, Azure Synapse, Databricks (batch ETL concept only; not Spark/distributed compute), Informatica, Talend, Fivetran, Matillion, Oracle EBS, SAP S4HANA Cloud, SAP Analytics Cloud, Power Query.
- **Framing guidance:** For BI / warehousing / ETL JDs that name adjacent tools, lead bullets with the concept ("Engineered ETL pipelines across 8+ financial workstreams...", "Optimised data warehouse query performance...", "Architected calculation views for real-time financial analysis...") and keep "SAP BW on HANA" as the technology qualifier at the end of the bullet, not the lead.

### Python (Accenture + projects + Monash coursework)
- **Concepts exercised:** data analytics using pandas, scikit-learn, Matplotlib; data wrangling; exploratory data analysis; supervised learning (Linear Regression, Random Forest) with log transformations, normalisation, missing-value handling; financial modelling with quadratic programming (cvxopt); image scraping and labelling for ML training; scripting for inference pipeline integration.
- **Evidence in career.md:** L24, L31, L80 (iNaturalist scraping), L139 (Linear Regression / Random Forest), L140 (time-series visualisation), L141 (BeautifulSoup), L142 (cvxopt portfolio optimisation), L154 (FIT9136).
- **Scope:** mixed - enterprise scripting, academic coursework, personal projects.
- **Adjacent tools:** R, Julia, MATLAB (MATLAB is *used* - see entry below), SAS, SPSS; for ML frameworks see PyTorch / TensorFlow entries below.
- **Framing guidance:** Python is broadly applicable; name it directly. For "data science" JDs, lead with analysis concepts (EDA, feature engineering) before naming libraries.

### Java (Accenture ambient + Monash coursework + Class Booking System assignment)
- **Concepts exercised:** OOP design with UML-driven Class & Sequence diagrams; unit testing; integrating multiple subsystems end-to-end (payment, admin modules); programming foundations.
- **Evidence in career.md:** L24, L138 (Class Booking System), L154 (FIT9131).
- **Scope:** coursework and one academic assignment. Not production.
- **Adjacent tools:** C#, Kotlin (Kotlin is *used* - see FreshMate entry), Scala, Go - typed/compiled general-purpose languages; Spring framework (not used).
- **Framing guidance:** For JDs asking for C#/Kotlin/Scala/Go, lead bullets with "OOP design", "UML-driven system design", "end-to-end subsystem integration" from the Class Booking System. Do NOT claim production Java work.

### TypeScript (BirdDex + AWS CDK + Hono backend)
- **Concepts exercised:** type-safe serverless backend development with Hono; infrastructure-as-code with AWS CDK (TypeScript); full-stack web development.
- **Evidence in career.md:** L24, L79 (Hono backend), L81 (CDK in TypeScript).
- **Scope:** production personal project (BirdDex is live with registered users).
- **Adjacent tools:** JavaScript (implicit), Deno, Bun (JS runtimes - not used).
- **Framing guidance:** Pair with "serverless backend" or "IaC" concepts depending on JD emphasis.

### SQL / PostgreSQL / Neon Postgres / MySQL (RDS)
- **Concepts exercised:** SQL query authoring and optimisation; relational schema design; data masking via SQL scripts; database migrations on deploy; cost-driven DB migration decisions (SAP HANA -> nothing; initial CDK DB -> Neon); production database operation.
- **Evidence in career.md:** L24, L31, L56 (SQL data masking), L79 / L81 (Neon Postgres on BirdDex), L85 (automated migrations), L93 (RDS MySQL on JobDetective), L118 (PostgreSQL in Public Transport project).
- **Scope:** multi-context - enterprise SQL at scale on HANA, production Postgres on a live web app, academic work with PostGIS.
- **Adjacent tools:** Oracle, SQL Server, MariaDB, CockroachDB, Aurora; DuckDB (not used).
- **Framing guidance:** SQL is broadly transferable. For "big data" JDs with Snowflake/BigQuery/Redshift, see SAP BW entry above for the bridging concepts.

### PostGIS (Public Transport Analysis - Melbourne, Monash project)
- **Concepts exercised:** spatial SQL; geospatial data integration (PTV GTFS + ABS suburb boundaries); spatial database schema design; spatial querying for urban transport analysis.
- **Evidence in career.md:** L31, L120, L121, L123.
- **Scope:** academic project.
- **Adjacent tools:** GeoPandas, Shapely, QGIS, ArcGIS, H3 (Uber), Google Earth Engine, Mapbox tiling - any geospatial toolchain.
- **Framing guidance:** Lead with "spatial SQL", "geospatial data integration", "spatial querying". Keep the "university project" framing.

### AWS - Lambda, API Gateway (HTTP API v2), S3, CloudFront, CDK, RDS (Accenture N/A; BirdDex + JobDetective + Pose Estimation API)
- **Concepts exercised:** serverless backend architecture; infrastructure-as-code; REST API design; presigned S3 upload flows; global CDN distribution; automated deploy pipelines; stack-level cost optimisation; cold-start tradeoff analysis; containerised Lambda (Docker, x86_64) for ML inference.
- **Evidence in career.md:** L24, L25, L38 (containerised Lambda for ML), L79 (Lambda + Hono + Neon), L80 (ONNX Runtime on containerised Lambda), L81 (CDK stack: HTTP API Gateway v2, Lambda, S3, CloudFront), L82 (cold start tradeoff), L85 (presigned S3, CloudFront, migrations on deploy), L93 (Lambda + RDS on JobDetective).
- **Scope:** multiple production personal projects + academic work.
- **Adjacent tools:** GCP (Cloud Functions, Cloud Run, GKE, BigQuery, Cloud Storage), Azure (Functions, App Service, Blob Storage, Cosmos DB); Terraform, Pulumi, Serverless Framework (different IaC tools; CDK is what's used); Cloudflare Workers (edge compute - not used); DynamoDB (not used - flag careful, was in careerv0 but removed from v2).
- **Framing guidance:** For GCP/Azure JDs, lead with "serverless architecture", "infrastructure-as-code", "REST API design", "CDN-backed static delivery". For Azure JDs, always include Microsoft Certified: Azure Data Engineer Associate (DP-203) in certifications, while keeping hands-on cloud examples tied to AWS unless `career.md` says otherwise. For Terraform/Pulumi JDs, lead with "infrastructure-as-code" and note AWS CDK specifically at the end.

### Docker (BirdDex + Pose Estimation + Public Transport local dev)
- **Concepts exercised:** containerised production workloads (Lambda-targeted); containerisation for academic ML API; local dev containers.
- **Evidence in career.md:** L25, L38, L80 (containerised Lambda), L110, L112, L118.
- **Scope:** production personal projects + academic.
- **Adjacent tools:** Podman, Buildah, containerd - same space.
- **Framing guidance:** Name Docker directly.

### Kubernetes (Pose Estimation REST API, Monash FIT5225 Cloud Computing)
- **Concepts exercised:** containerised ML API deployment on K8s under strict CPU/memory resource constraints; load and performance testing with Locust; horizontal scaling strategy informed by per-pod resource limits.
- **Evidence in career.md:** L38, L110, L112, L113.
- **Scope:** academic project only. Not production. Scope flag matters.
- **Adjacent tools:** EKS / GKE / AKS (managed K8s), OpenShift, ECS / Fargate (container orchestration without K8s); Helm, Kustomize (not referenced in career.md - avoid claiming).
- **Framing guidance:** For K8s JDs, acceptable to name Kubernetes but keep the "academic / resource-constrained" context intact. Lead with "containerisation", "horizontal scaling strategy", "load testing" concepts. Don't imply production operations experience.

### Vue 3 / Vite / Tailwind CSS / PrimeVue (BirdDex, JobDetective, Project Demeter)
- **Concepts exercised:** full-stack web development; responsive frontend development; component libraries; Vite build tooling; utility-first CSS.
- **Evidence in career.md:** L79, L81, L83, L93, L102.
- **Scope:** three personal projects, one live with users.
- **Adjacent tools:** React (Next.js, Remix, Vite-React), Svelte / SvelteKit, Angular, Solid, Nuxt - all component-based SPA frameworks.
- **Framing guidance:** For React/Angular/Svelte JDs, lead with "full-stack web development", "responsive frontend", "component-based UI" and name Vue 3 at the technology qualifier position. Do not claim React experience.

### FastAPI / Hono (Pose Estimation API + BirdDex)
- **Concepts exercised:** RESTful API design; type-safe API development; lightweight serverless-compatible backend frameworks.
- **Evidence in career.md:** L24, L79, L110.
- **Scope:** one academic API + one production personal project.
- **Adjacent tools:** Flask, Django, Express, NestJS, Koa, Fastify, Elysia, Bun HTTP, Gin (Go), Spring Boot (Java).
- **Framing guidance:** Lead with "REST API design" for unfamiliar framework JDs.

### Firebase (Firestore, Auth) + better-auth + OAuth + Resend + SendGrid
- **Concepts exercised:** authentication flows (email/password, Google OAuth, email verification, password reset); transactional and bulk email; Firestore data modelling with custom security rules and indexing.
- **Evidence in career.md:** L84, L100, L104, L105, L133.
- **Adjacent tools:** Auth0, Clerk, Supabase Auth, AWS Cognito, NextAuth; Postmark, Mailgun, AWS SES.
- **Framing guidance:** Lead with "authentication flows" or "transactional email pipelines"; swap tool names out.

### OpenAI API (JobDetective, Project Demeter)
- **Concepts exercised:** LLM integration with custom system instructions; analysis-pipeline design combining OCR with LLM reasoning; personalised content generation from user inputs.
- **Evidence in career.md:** L92, L103.
- **Scope:** two personal projects.
- **Adjacent tools:** Anthropic Claude API, Google Gemini API, Cohere, Mistral; LangChain, LlamaIndex, Haystack (orchestration frameworks - not used); Hugging Face Inference (not used).
- **Framing guidance:** Lead with "LLM integration", "prompt design with system instructions", "analysis pipeline design". For LangChain JDs specifically, lead with "LLM-assisted analysis pipeline" and do not claim LangChain.

### YOLO / YOLOv8 / ONNX Runtime / TensorFlow Lite (BirdDex, FreshMate, Pose Estimation)
- **Concepts exercised:** object detection model fine-tuning; model export to ONNX for serverless inference; on-device ML (TensorFlow Lite); classification across 36 species; containerised inference deployment.
- **Evidence in career.md:** L38, L39, L40, L80, L110, L112, L130.
- **Scope:** three personal / academic projects.
- **Adjacent tools:** PyTorch (ecosystem adjacent - ONNX interop), TensorFlow full (adjacent to TF Lite), Detectron2, MMDetection; Roboflow (MLOps); MediaPipe.
- **Framing guidance:** For PyTorch JDs, lead with "object detection model fine-tuning", "model export and serving", "containerised inference". Do not claim PyTorch specifically unless user confirms it was in the training loop.

### Tableau (Accenture reporting ambient + JobDetective embedded dashboards)
- **Concepts exercised:** embedded dashboards for real-time analytics; operational and financial reporting.
- **Evidence in career.md:** L33, L94.
- **Scope:** Accenture reporting layer + one personal project.
- **Adjacent tools:** PowerBI, Looker Studio, Looker, Qlik, Metabase, Superset.
- **Framing guidance:** Tableau is named. For PowerBI/Looker JDs, lead with "embedded analytics dashboards" or "operational reporting" and pair with SAP BW warehousing concepts for depth.

### Locust (Pose Estimation API load testing)
- **Concepts exercised:** load and performance testing; concurrency limit evaluation; scaling strategy decisions informed by test results.
- **Evidence in career.md:** L40, L113.
- **Scope:** academic.
- **Adjacent tools:** k6, JMeter, Gatling, Artillery, wrk.
- **Framing guidance:** Lead with "load and performance testing" concept.

### Kotlin (FreshMate Android app)
- **Concepts exercised:** native Android development; Firebase Auth / Firestore integration; on-device TFLite integration; weather API integration; 4-member team delivery.
- **Evidence in career.md:** L127, L129, L130, L131, L133, L134.
- **Scope:** capstone project (FIT5046).
- **Adjacent tools:** Java (used - see above), Swift (iOS - not used), Flutter / Dart, React Native (not used).
- **Framing guidance:** For Android JDs, acceptable to name Kotlin. For cross-platform mobile JDs, lead with "mobile application development", "on-device ML integration", "authenticated mobile data flows".

### Jira / Confluence / ServiceNow (Accenture)
- **Concepts exercised:** ticket and change workflows; knowledge-base authoring; incident and change request handling; end-to-end change ownership.
- **Evidence in career.md:** L53.
- **Adjacent tools:** Linear, Asana, Monday, Notion, PagerDuty, Opsgenie, Freshservice, BMC Remedy.
- **Framing guidance:** Lead with "ticket and change workflow management", "knowledge-base authoring", "incident ownership".

### MATLAB / Simulink (B.Tech final project)
- **Concepts exercised:** modelling physical systems (solar-powered water pump); MPPT algorithm implementation for energy harvesting.
- **Evidence in career.md:** L143, L162.
- **Scope:** B.Tech academic project.
- **Framing guidance:** Relevant only for niche control-systems / simulation JDs. Keep "B.Tech final project" scope.

### Git / branch-based workflows (FreshMate, Accenture ambient)
- **Concepts exercised:** branch-based parallel feature development; team-of-4 collaboration.
- **Evidence in career.md:** L134.
- **Framing guidance:** Assume baseline; don't foreground unless JD explicitly calls out Git workflow discipline.

---

## 2. Concept -> Bullets Index (reverse lookup)

When a JD keyword matches one of these concepts, pull bullets from the cited lines.

- **Enterprise ETL / data pipelines:** L54, L57, L62.
- **Data warehousing / dimensional modelling / OLAP / calculation views:** L52, L62, L64, L65.
- **SQL query optimisation:** L55, L63.
- **Root cause analysis on production data systems:** L63.
- **GDPR / data compliance / data masking:** L56.
- **Testing discipline (UT / SIT / UAT):** L57.
- **Release management / end-to-end delivery:** L66.
- **Agile / DevOps collaboration / technical risk assessment:** L26, L67.
- **Stakeholder management / status reporting:** L58, L69.
- **Mentoring / onboarding:** L68.
- **Incident / change workflow ownership:** L53.
- **Serverless architecture (Lambda + API Gateway):** L24, L25, L79, L93.
- **Infrastructure-as-code (AWS CDK):** L25, L81.
- **Containerisation (Docker):** L25, L80, L112, L118.
- **Container orchestration / K8s (academic, resource-constrained):** L38, L112, L113.
- **Presigned S3 upload flows / CDN distribution:** L85.
- **Cost-driven architecture decisions / cold start tradeoff:** L81, L82.
- **REST API design:** L79, L93, L108, L112.
- **Full-stack web development (Vue 3):** L79, L83, L93, L102.
- **Authentication flows (OAuth, email verification, password reset):** L84, L133.
- **Transactional / bulk email:** L84, L105.
- **Object detection / computer vision:** L38, L80 (BirdDex, 36 species), L112 (pose estimation), L130 (pantry object detection).
- **Model fine-tuning and ONNX export for inference:** L80.
- **On-device ML (TFLite):** L38, L130.
- **LLM integration / prompt engineering / analysis pipelines:** L92 (scam detection), L103 (meal plan generation).
- **OCR / multi-modal input processing:** L92.
- **RAG / vector DB (planned, not built - frame as roadmap familiarity):** L96.
- **Load / performance testing (Locust):** L40, L113.
- **Horizontal scaling strategy decisions:** L113.
- **Spatial SQL / PostGIS / geospatial analysis:** L120, L121.
- **Data wrangling / EDA / data quality:** L32.
- **Feature engineering / preprocessing (log transforms, normalisation, missing values):** L139.
- **Supervised learning (Linear Regression, Random Forest):** L139.
- **Financial modelling / portfolio optimisation (cvxopt):** L142.
- **Time series visualisation:** L140.
- **OOP / UML design:** L138.
- **Mobile development (native Android, Kotlin):** L127, L129, L131, L133.
- **4-person team delivery / branch-based workflow:** L134.
- **Embedded analytics / Tableau dashboards:** L33, L94.
- **Self-service reporting enablement (SAP BEx):** L65.

---

## 3. Adjacent Tool -> Concept Map (reverse lookup)

For JD keywords that name a tool Aditya has NOT used. Lead relevant bullets with the listed concepts. **Never put the adjacent tool in the rendered output.**

### BI / Analytics
- **PowerBI, Looker, Looker Studio, Qlik, Metabase, Superset** -> dimensional modelling, calculation view design, embedded analytics dashboards, operational and financial reporting. Source work: SAP BW + Tableau. (Tableau IS used; can be named alongside concepts.)

### Data warehouses
- **Snowflake, BigQuery, Redshift, Azure Synapse, Oracle Autonomous DW** -> columnar data warehousing, calculation views, ETL orchestration, query optimisation, self-service reporting. Source work: SAP BW on HANA.

### ETL / orchestration
- **dbt, Airflow, Prefect, Dagster, Informatica, Talend, Fivetran, Matillion, Glue** -> ETL pipeline development and maintenance, month-end orchestration across financial workstreams, batch and real-time integration, Process Chain automation. Source work: SAP BW + SAP Process Chains.

### Distributed compute (flag with care - Aditya has NOT done distributed/parallel compute)
- **Spark, Databricks, Flink, Hadoop, Dask, Ray** -> batch ETL concepts and enterprise data pipeline scale only. Do NOT imply distributed-compute experience. Usually safer to skip than to stretch.

### Programming languages (not used)
- **C#** -> OOP design, typed-language fluency, end-to-end subsystem integration (Class Booking System). Source work: Java coursework + assignment.
- **Scala, Go** -> same concepts as above. Keep scope honest: Java is coursework, not production.
- **Rust** -> do not stretch. No C/C++/systems-programming evidence in career.md.
- **PHP, Ruby** -> do not stretch.
- **R** -> statistical analysis, supervised learning, EDA. Source work: Python analytics (pandas / scikit-learn) + Monash coursework.

### Frontend frameworks (not used)
- **React, Next.js, Remix, Svelte, SvelteKit, Angular, Solid, Nuxt** -> full-stack web development, responsive frontend, component-based SPAs, Vite build tooling. Source work: Vue 3 across BirdDex / JobDetective / Project Demeter.

### Backend frameworks (not used)
- **Flask, Django, Express, NestJS, Koa, Fastify, Elysia, Spring Boot, Gin** -> REST API design, serverless-compatible backends, type-safe API development. Source work: FastAPI + Hono.

### Cloud providers (not used in production)
- **GCP (Cloud Functions, Cloud Run, GKE, Cloud Storage, BigQuery, Pub/Sub)** -> serverless architecture, IaC, REST API design, managed container orchestration, CDN delivery. Source work: AWS (Lambda, API Gateway, S3, CloudFront, CDK).
- **Azure (Functions, App Service, Blob Storage, Cosmos DB, Synapse, AKS)** -> same concepts. Additionally: Aditya holds Microsoft Certified: Azure Data Engineer Associate (DP-203) per `career.md`; include it for Azure-relevant roles. The certification supports Azure relevance, but do not imply hands-on production delivery with Azure services unless that experience appears in `career.md`.

### IaC (not used - CDK is used)
- **Terraform, Pulumi, Serverless Framework, CloudFormation (direct), Ansible** -> infrastructure-as-code, stack-level deployments, cost-driven architecture decisions. Source work: AWS CDK (TypeScript).

### NoSQL / KV / cache (caution - limited exposure)
- **DynamoDB, MongoDB, Cassandra, Redis, Memcached, Elasticsearch, OpenSearch** -> be careful. Aditya has Firestore (document DB) experience and Postgres experience. Only reframe if the JD wants general "NoSQL / document DB" exposure. Source work: Firebase Firestore with custom security rules and indexing (L104).

### Messaging / streaming (not used)
- **Kafka, RabbitMQ, AWS SQS, Kinesis, Pub/Sub, Event Hubs** -> do NOT stretch. No streaming / event-driven evidence in career.md. Skip or mention "real-time data integration" from SAP BW only when genuinely applicable.

### ML frameworks (not used directly - ONNX interop exists)
- **PyTorch** -> object detection model fine-tuning and export, containerised inference, on-device ML. Source work: YOLO training + ONNX Runtime + TFLite. Do not claim PyTorch training loops directly.
- **TensorFlow (full)** -> on-device ML, model integration. Source work: TensorFlow Lite (FreshMate).
- **scikit-learn** -> IS used; see Python entry.
- **Hugging Face Transformers, LangChain, LlamaIndex, Haystack** -> LLM integration, prompt design, analysis pipeline design. Source work: OpenAI API (JobDetective, Project Demeter).

### Vector DBs / RAG (planned, not built)
- **Pinecone, Weaviate, Chroma, Qdrant, Milvus, pgvector** -> MVP roadmap familiarity only (L96). Frame as "designed for future RAG-based evolution" - never imply shipped.

### Observability / CI-CD (limited)
- **Prometheus, Grafana, Datadog, New Relic, Sentry** -> do not stretch unless evidence added to career.md.
- **GitHub Actions, GitLab CI, Jenkins, CircleCI, Buildkite** -> "automated deployment pipelines" (L25) is thin evidence; caution. Prefer to skip unless user confirms.

### Mobile (cross-platform, not used)
- **Flutter / Dart, React Native, Swift / iOS** -> mobile application development, on-device ML, authenticated mobile data flows. Source work: Kotlin + FreshMate (capstone).

### Ticketing / ITSM (adjacent to Jira / Confluence / ServiceNow - used)
- **Linear, Asana, Monday, PagerDuty, Opsgenie** -> ticket and change workflow management, incident ownership, knowledge-base authoring. Source work: Accenture.

---

## Maintenance notes

- Whenever `career.md` changes, re-check the line citations in this file.
- If you add a new project or role, add a new Tool -> Concepts entry and update the Concept -> Bullets Index.
- If a JD repeatedly names a tool that isn't in the Adjacent Tool map, add it (with honest framing guidance) rather than stretching during generation.
