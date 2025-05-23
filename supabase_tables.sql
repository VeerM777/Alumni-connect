-- Authentication is handled by Supabase Auth, but we need a users table to match Django's
CREATE TABLE IF NOT EXISTS auth_user (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Enable RLS
ALTER TABLE auth_user ENABLE ROW LEVEL SECURITY;

-- Alumni Profiles
CREATE TABLE IF NOT EXISTS alumni_profile (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id UUID REFERENCES auth_user(id) ON DELETE CASCADE,
    graduation_year INT,
    degree VARCHAR(100) DEFAULT '',
    department VARCHAR(100) DEFAULT '',
    current_company VARCHAR(200) DEFAULT '',
    job_title VARCHAR(100) DEFAULT '',
    location VARCHAR(100),
    expertise VARCHAR(200) DEFAULT '',
    years_of_experience INT DEFAULT 0,
    mentoring_preference VARCHAR(50) DEFAULT '',
    availability VARCHAR(10) DEFAULT '',
    linkedin_profile VARCHAR(200),
    bio TEXT DEFAULT '',
    profile_picture_url VARCHAR(255),
    is_available_for_mentoring BOOLEAN DEFAULT FALSE
);

-- Enable RLS
ALTER TABLE alumni_profile ENABLE ROW LEVEL SECURITY;

-- Student Profiles
CREATE TABLE IF NOT EXISTS student_profile (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id UUID REFERENCES auth_user(id) ON DELETE CASCADE,
    enrollment_year INT,
    degree_pursuing VARCHAR(100) DEFAULT '',
    department VARCHAR(100) DEFAULT '',
    expected_graduation INT,
    profile_picture_url VARCHAR(255)
);

-- Allow users to access their own data
CREATE POLICY "Users can access their own data" ON student_profile
FOR SELECT
USING (auth.uid() = user_id);

-- Teacher Profiles
CREATE TABLE IF NOT EXISTS teacher_profile (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id UUID REFERENCES auth_user(id) ON DELETE CASCADE,
    department VARCHAR(100) DEFAULT '',
    position VARCHAR(50) DEFAULT '',
    specialization VARCHAR(200) DEFAULT '',
    teaching_experience INT DEFAULT 0,
    highest_degree VARCHAR(50) DEFAULT '',
    degree_year INT,
    degree_institution VARCHAR(200) DEFAULT '',
    bio TEXT DEFAULT '',
    profile_picture_url VARCHAR(255),
    available_for_advising BOOLEAN DEFAULT FALSE
);

-- Events
CREATE TABLE IF NOT EXISTS event (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    date TIMESTAMPTZ NOT NULL,
    location VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    organizer_id UUID REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Event Registrations
CREATE TABLE IF NOT EXISTS event_registration (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    event_id BIGINT REFERENCES event(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth_user(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(event_id, user_id)
);

-- Add constraints and relationships
ALTER TABLE event_registration ADD CONSTRAINT fk_event FOREIGN KEY (event_id) REFERENCES event(id) ON DELETE CASCADE;
ALTER TABLE event_registration ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE;

-- Mentorship Requests
CREATE TABLE IF NOT EXISTS mentorship_request (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    student_id UUID REFERENCES auth_user(id) ON DELETE CASCADE,
    alumni_id UUID REFERENCES auth_user(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    topic VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Career Updates
CREATE TABLE IF NOT EXISTS career_update (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    alumni_id UUID REFERENCES auth_user(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE
);

-- Messages
CREATE TABLE IF NOT EXISTS message (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Notifications
CREATE TABLE IF NOT EXISTS notification (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    notification_type VARCHAR(20) NOT NULL,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    recipient_id UUID REFERENCES auth_user(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES auth_user(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read BOOLEAN NOT NULL DEFAULT FALSE,
    related_link VARCHAR(200)
);

-- Create Row Level Security Policies
ALTER TABLE alumni_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE teacher_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE event ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_registration ENABLE ROW LEVEL SECURITY;
ALTER TABLE mentorship_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_update ENABLE ROW LEVEL SECURITY;
ALTER TABLE message ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification ENABLE ROW LEVEL SECURITY;

-- Sample policy allowing authenticated users to read data
CREATE POLICY "Users can read all alumni profiles" ON alumni_profile FOR SELECT USING (true);

-- Ensure all user_id fields are UUID
ALTER TABLE student_profile ALTER COLUMN user_id TYPE UUID USING user_id::uuid;
ALTER TABLE alumni_profile ALTER COLUMN user_id TYPE UUID USING user_id::uuid;
ALTER TABLE teacher_profile ALTER COLUMN user_id TYPE UUID USING user_id::uuid;
ALTER TABLE event_registration ALTER COLUMN user_id TYPE UUID USING user_id::uuid;
ALTER TABLE mentorship_request ALTER COLUMN student_id TYPE UUID USING student_id::uuid;
ALTER TABLE mentorship_request ALTER COLUMN alumni_id TYPE UUID USING alumni_id::uuid;