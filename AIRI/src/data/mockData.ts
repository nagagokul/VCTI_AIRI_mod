
export const USERS = [
  { id: 1, username: "admin",     password: "admin123", name: "Alex Carter",  role: "Admin",     initials: "AC" },
  { id: 2, username: "recruiter", password: "recruit1", name: "Jamie Reeves", role: "Recruiter", initials: "JR" },
];


export const CANDIDATES = [
  {
    id: 1, name: "Sophia Chen", role: "Senior Frontend Engineer",
    status: "Interview", score: 94,
    skills: ["React", "TypeScript", "GraphQL", "Next.js"],
    location: "San Francisco, CA", experience: "7 yrs",
    applied: "Feb 12, 2026", email: "sophia@email.com", department: "Engineering",
  },
  {
    id: 2, name: "Marcus Williams", role: "ML Engineer",
    status: "Screening", score: 88,
    skills: ["Python", "PyTorch", "MLOps", "AWS"],
    location: "New York, NY", experience: "5 yrs",
    applied: "Feb 14, 2026", email: "marcus@email.com", department: "Data Science",
  },
  {
    id: 3, name: "Priya Sharma", role: "DevOps Engineer",
    status: "Offer", score: 97,
    skills: ["Kubernetes", "Terraform", "AWS", "CI/CD"],
    location: "Austin, TX", experience: "9 yrs",
    applied: "Feb 8, 2026", email: "priya@email.com", department: "Infrastructure",
  },
  {
    id: 4, name: "Jordan Blake", role: "Product Manager",
    status: "Rejected", score: 61,
    skills: ["Roadmapping", "Agile", "SQL", "Figma"],
    location: "Chicago, IL", experience: "4 yrs",
    applied: "Feb 10, 2026", email: "jordan@email.com", department: "Product",
  },
  {
    id: 5, name: "Elena Rossi", role: "Backend Engineer",
    status: "Interview", score: 91,
    skills: ["Go", "PostgreSQL", "Redis", "gRPC"],
    location: "Remote", experience: "6 yrs",
    applied: "Feb 15, 2026", email: "elena@email.com", department: "Engineering",
  },
  {
    id: 6, name: "Kwame Asante", role: "Data Scientist",
    status: "Screening", score: 85,
    skills: ["R", "Spark", "TensorFlow", "SQL"],
    location: "Seattle, WA", experience: "3 yrs",
    applied: "Feb 16, 2026", email: "kwame@email.com", department: "Data Science",
  },
  {
    id: 7, name: "Lily Zhang", role: "UX Designer",
    status: "Offer", score: 93,
    skills: ["Figma", "User Research", "Prototyping", "CSS"],
    location: "Los Angeles, CA", experience: "5 yrs",
    applied: "Feb 11, 2026", email: "lily@email.com", department: "Design",
  },
  {
    id: 8, name: "Rafi Hassan", role: "Security Engineer",
    status: "Interview", score: 89,
    skills: ["Pen Testing", "SIEM", "Zero Trust", "SAST"],
    location: "Boston, MA", experience: "8 yrs",
    applied: "Feb 13, 2026", email: "rafi@email.com", department: "Security",
  },
  {
    id: 9, name: "Nadia Kovacs", role: "Engineering Manager",
    status: "Screening", score: 82,
    skills: ["Leadership", "Java", "System Design", "Agile"],
    location: "Denver, CO", experience: "11 yrs",
    applied: "Feb 17, 2026", email: "nadia@email.com", department: "Engineering",
  },
  {
    id: 10, name: "Tomás Rivera", role: "Cloud Architect",
    status: "Offer", score: 96,
    skills: ["Azure", "GCP", "Microservices", "Kafka"],
    location: "Miami, FL", experience: "10 yrs",
    applied: "Feb 9, 2026", email: "tomas@email.com", department: "Infrastructure",
  },
  {
  id: 11,
  name: "Arjun Mehta",
  role: "Frontend Engineer",
  status: "Screening",
  score: 90,
  skills: ["React", "JavaScript", "TypeScript", "Redux"],
  location: "Dallas, TX",
  experience: "5 yrs",
  applied: "Feb 18, 2026",
  email: "arjun@email.com",
  department: "Engineering",
},
{
  id: 12,
  name: "Emily Johnson",
  role: "Senior Frontend Engineer",
  status: "Interview",
  score: 92,
  skills: ["React", "Next.js", "GraphQL", "CSS"],
  location: "San Diego, CA",
  experience: "8 yrs",
  applied: "Feb 18, 2026",
  email: "emily@email.com",
  department: "Engineering",
},
{
  id: 13,
  name: "Daniel Kim",
  role: "Backend Engineer",
  status: "Screening",
  score: 87,
  skills: ["Node.js", "PostgreSQL", "AWS", "Redis"],
  location: "Atlanta, GA",
  experience: "6 yrs",
  applied: "Feb 19, 2026",
  email: "daniel@email.com",
  department: "Engineering",
},
{
  id: 14,
  name: "Fatima Noor",
  role: "ML Engineer",
  status: "Interview",
  score: 91,
  skills: ["Python", "TensorFlow", "AWS", "MLOps"],
  location: "Remote",
  experience: "6 yrs",
  applied: "Feb 19, 2026",
  email: "fatima@email.com",
  department: "Data Science",
},
{
  id: 15,
  name: "Carlos Mendes",
  role: "DevOps Engineer",
  status: "Screening",
  score: 88,
  skills: ["Kubernetes", "AWS", "Terraform", "Docker"],
  location: "Phoenix, AZ",
  experience: "7 yrs",
  applied: "Feb 20, 2026",
  email: "carlos@email.com",
  department: "Infrastructure",
},
{
  id: 16,
  name: "Aisha Rahman",
  role: "Data Scientist",
  status: "Offer",
  score: 93,
  skills: ["Python", "SQL", "Spark", "Machine Learning"],
  location: "Remote",
  experience: "5 yrs",
  applied: "Feb 20, 2026",
  email: "aisha@email.com",
  department: "Data Science",
},
{
  id: 17,
  name: "Michael Brown",
  role: "Full Stack Engineer",
  status: "Interview",
  score: 89,
  skills: ["React", "Node.js", "AWS", "MongoDB"],
  location: "San Jose, CA",
  experience: "6 yrs",
  applied: "Feb 21, 2026",
  email: "michael@email.com",
  department: "Engineering",
},
{
  id: 18,
  name: "Sven Richter",
  role: "Cloud Engineer",
  status: "Screening",
  score: 86,
  skills: ["AWS", "Azure", "Docker", "CI/CD"],
  location: "Remote",
  experience: "7 yrs",
  applied: "Feb 21, 2026",
  email: "sven@email.com",
  department: "Infrastructure",
},
{
  id: 19,
  name: "Hannah Lee",
  role: "Frontend Developer",
  status: "Interview",
  score: 88,
  skills: ["React", "TypeScript", "CSS", "Figma"],
  location: "Portland, OR",
  experience: "4 yrs",
  applied: "Feb 22, 2026",
  email: "hannah@email.com",
  department: "Engineering",
},
{
  id: 20,
  name: "Victor Alvarez",
  role: "Software Engineer",
  status: "Screening",
  score: 84,
  skills: ["Java", "Spring Boot", "AWS", "Microservices"],
  location: "Houston, TX",
  experience: "6 yrs",
  applied: "Feb 22, 2026",
  email: "victor@email.com",
  department: "Engineering",
},
];


export const PIPELINE = [
  { stage: "Applied",   count: 248, color: "#60a5fa" },
  { stage: "Screening", count: 131, color: "#a78bfa" },
  { stage: "Interview", count: 62,  color: "#34d399" },
  { stage: "Offer",     count: 12,  color: "#fbbf24" },
  { stage: "Hired",     count: 8,   color: "#f472b6" },
];


export const WEEKLY_APPS = [42, 58, 37, 71, 65, 88, 54];
export const DAYS        = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];


export const STATUS_CONFIG = {
  Interview: {
    color:  "text-sky-300",
    bg:     "bg-sky-500/15",
    border: "border-sky-500/30",
    dot:    "bg-sky-400",
  },
  Screening: {
    color:  "text-violet-300",
    bg:     "bg-violet-500/15",
    border: "border-violet-500/30",
    dot:    "bg-violet-400",
  },
  Offer: {
    color:  "text-emerald-300",
    bg:     "bg-emerald-500/15",
    border: "border-emerald-500/30",
    dot:    "bg-emerald-400",
  },
  Rejected: {
    color:  "text-red-300",
    bg:     "bg-red-500/15",
    border: "border-red-500/30",
    dot:    "bg-red-400",
  },
  Hired: {
    color:  "text-amber-300",
    bg:     "bg-amber-500/15",
    border: "border-amber-500/30",
    dot:    "bg-amber-400",
  },
};

// ─────────────────────────────────────────────
// CHATBOT MOCK RESPONSES
// ─────────────────────────────────────────────
export const BOT_RESPONSES = [
  "I've analyzed the uploaded resume. The candidate shows a **94% skill match** on core competencies for your Senior Engineer requirements. I recommend fast-tracking to technical interview.",
  "Based on current pipeline data, your average time-to-hire is **21 days** — down 3 days from Q4 2025. Accelerating the offer stage for high-score candidates could reduce drop-off by ~18%.",
  "I found **3 strong candidates** in the database matching your DevOps criteria. Priya Sharma scores highest at 97 with hands-on Kubernetes and Terraform expertise.",
  "Your Q1 hiring velocity is up **12% vs Q4 2025**. The ML Engineer pipeline is currently your bottleneck — consider broadening initial screening criteria to include adjacent skills.",
  "Sourcing analysis shows referral hires have a **34% lower time-to-hire** and 28% better 6-month retention rate compared to LinkedIn hires. I'd recommend scaling your referral program.",
  "I've parsed the job description successfully. Cross-referencing against our internal candidate database now — I found **7 potential matches** with 80%+ compatibility scores.",
];

// ─────────────────────────────────────────────
// DASHBOARD KPIs
// ─────────────────────────────────────────────
export const DASHBOARD_KPIS = [
  { label: "Total Candidates", value: "248",   sub: "↑ 12% vs last month",    color: "#60a5fa", hasSparkline: true },
  { label: "Active Openings",  value: "34",    sub: "Across 8 departments",   color: "#a78bfa", hasSparkline: false },
  { label: "Hire Rate",        value: "18.4%", sub: "↑ 2.1% this quarter",    color: "#34d399", hasSparkline: false },
  { label: "Avg Time to Hire", value: "21d",   sub: "↓ 3 days vs Q4",         color: "#fbbf24", hasSparkline: false },
  { label: "Offers Extended",  value: "12",    sub: "8 accepted · 4 pending", color: "#f472b6", hasSparkline: false },
  { label: "Screening Pass",   value: "73%",   sub: "AI-assisted filtering",  color: "#38bdf8", hasSparkline: false },
];

export const TOP_ROLES = [
  { role: "Senior Engineer", openings: 8,  applicants: 74 },
  { role: "ML Engineer",     openings: 5,  applicants: 61 },
  { role: "Product Manager", openings: 4,  applicants: 38 },
  { role: "DevOps / SRE",    openings: 3,  applicants: 29 },
  { role: "UX Designer",     openings: 2,  applicants: 46 },
];

export const SOURCING_CHANNELS = [
  { name: "LinkedIn",     pct: 38, color: "#60a5fa" },
  { name: "Referral",     pct: 27, color: "#a78bfa" },
  { name: "Direct Apply", pct: 18, color: "#34d399" },
  { name: "GitHub Jobs",  pct: 11, color: "#fbbf24" },
  { name: "Other",        pct: 6,  color: "#94a3b8" },
];
