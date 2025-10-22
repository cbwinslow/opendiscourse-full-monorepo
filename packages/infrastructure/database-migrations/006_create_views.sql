-- Migration 006_create_views.sql
-- Create views that combine data from multiple sources

-- View for legislator profiles combining all data sources
CREATE OR REPLACE VIEW legislator_profiles AS
SELECT 
    ml.id,
    ml.bioguide_id,
    ml.full_name,
    ml.first_name,
    ml.last_name,
    ml.gender,
    ml.date_of_birth,
    ml.party,
    ml.state,
    ml.chamber,
    ml.district,
    ml.in_office,
    ml.twitter_account,
    ml.facebook_account,
    ml.youtube_account,
    ml.website_url,
    ml.contact_form,
    ml.office_address,
    ml.phone,
    -- KPI scores
    COALESCE(mk_truth.score, 0) as truthfulness_score,
    COALESCE(mk_consistency.score, 0) as consistency_score,
    COALESCE(mk_engagement.score, 0) as engagement_score,
    -- Social media activity
    COALESCE(social_counts.post_count, 0) as social_post_count,
    COALESCE(social_counts.total_likes, 0) as social_total_likes,
    COALESCE(social_counts.total_shares, 0) as social_total_shares,
    -- Voting statistics
    COALESCE(vote_stats.total_votes, 0) as total_votes,
    COALESCE(vote_stats.yes_votes, 0) as yes_votes,
    COALESCE(vote_stats.no_votes, 0) as no_votes,
    COALESCE(vote_stats.absent_votes, 0) as absent_votes,
    COALESCE(vote_stats.party_line_votes, 0) as party_line_votes,
    -- Bill sponsorship
    COALESCE(bill_stats.sponsored_bills, 0) as sponsored_bills,
    COALESCE(bill_stats.cosponsored_bills, 0) as cosponsored_bills,
    ml.created_at,
    ml.updated_at
FROM master_legislators ml
LEFT JOIN master_kpi_scores mk_truth ON ml.id = mk_truth.legislator_id AND mk_truth.metric_name = 'truthfulness'
LEFT JOIN master_kpi_scores mk_consistency ON ml.id = mk_consistency.legislator_id AND mk_consistency.metric_name = 'consistency'
LEFT JOIN master_kpi_scores mk_engagement ON ml.id = mk_engagement.legislator_id AND mk_engagement.metric_name = 'engagement'
LEFT JOIN (
    SELECT 
        legislator_id,
        COUNT(*) as post_count,
        SUM(likes) as total_likes,
        SUM(shares) as total_shares
    FROM master_social_media_posts
    GROUP BY legislator_id
) social_counts ON ml.id = social_counts.legislator_id
LEFT JOIN (
    SELECT 
        legislator_id,
        COUNT(*) as total_votes,
        COUNT(CASE WHEN vote_position = 'yes' THEN 1 END) as yes_votes,
        COUNT(CASE WHEN vote_position = 'no' THEN 1 END) as no_votes,
        COUNT(CASE WHEN vote_position = 'absent' THEN 1 END) as absent_votes,
        COUNT(CASE WHEN vote_position IN ('yes', 'no') AND 
                   ((party = 'Republican' AND vote_position = 'yes') OR 
                    (party = 'Democrat' AND vote_position = 'no')) THEN 1 END) as party_line_votes
    FROM master_votes mv
    JOIN master_legislators ml2 ON mv.legislator_id = ml2.id
    GROUP BY legislator_id
) vote_stats ON ml.id = vote_stats.legislator_id
LEFT JOIN (
    SELECT 
        sponsor_id,
        COUNT(*) as sponsored_bills,
        SUM(cosponsor_count) as cosponsored_bills
    FROM master_bills mb
    LEFT JOIN (
        SELECT bill_id, COUNT(*) as cosponsor_count
        FROM master_votes
        WHERE vote_position = 'cosponsor'
        GROUP BY bill_id
    ) cosponsors ON mb.id = cosponsors.bill_id
    WHERE sponsor_id IS NOT NULL
    GROUP BY sponsor_id
) bill_stats ON ml.id = bill_stats.sponsor_id;

-- View for bill details with sponsor and vote information
CREATE OR REPLACE VIEW bill_details AS
SELECT 
    mb.id,
    mb.bill_id,
    mb.bill_type,
    mb.bill_number,
    mb.congress_number,
    mb.state,
    mb.jurisdiction,
    mb.title,
    mb.short_title,
    mb.summary,
    mb.introduced_date,
    mb.sponsor_name,
    ml.full_name as sponsor_full_name,
    mb.committees,
    mb.primary_subject,
    mb.latest_action_date,
    mb.latest_action,
    mb.house_passage,
    mb.senate_passage,
    mb.enacted_date,
    mb.vetoed_date,
    mb.active,
    -- Vote counts
    COALESCE(vote_counts.yes_votes, 0) as yes_votes,
    COALESCE(vote_counts.no_votes, 0) as no_votes,
    COALESCE(vote_counts.absent_votes, 0) as absent_votes,
    COALESCE(vote_counts.total_votes, 0) as total_votes,
    -- Cosponsor counts
    COALESCE(cosponsor_counts.cosponsor_count, 0) as cosponsor_count,
    mb.created_at,
    mb.updated_at
FROM master_bills mb
LEFT JOIN master_legislators ml ON mb.sponsor_id = ml.id
LEFT JOIN (
    SELECT 
        bill_id,
        COUNT(CASE WHEN vote_position = 'yes' THEN 1 END) as yes_votes,
        COUNT(CASE WHEN vote_position = 'no' THEN 1 END) as no_votes,
        COUNT(CASE WHEN vote_position = 'absent' THEN 1 END) as absent_votes,
        COUNT(*) as total_votes
    FROM master_votes
    WHERE vote_position IN ('yes', 'no', 'absent')
    GROUP BY bill_id
) vote_counts ON mb.id = vote_counts.bill_id
LEFT JOIN (
    SELECT 
        bill_id,
        COUNT(*) as cosponsor_count
    FROM master_votes
    WHERE vote_position = 'cosponsor'
    GROUP BY bill_id
) cosponsor_counts ON mb.id = cosponsor_counts.bill_id;

-- View for recent activity feed
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    'bill' as activity_type,
    mb.id as subject_id,
    mb.title as subject_title,
    mb.latest_action_date as activity_date,
    mb.latest_action as activity_description,
    mb.state as jurisdiction,
    NULL as legislator_id,
    NULL as legislator_name
FROM master_bills mb
WHERE mb.latest_action_date >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT 
    'vote' as activity_type,
    mv.id as subject_id,
    mb.title as subject_title,
    mv.vote_date as activity_date,
    mv.motion_text as activity_description,
    mb.state as jurisdiction,
    mv.legislator_id,
    ml.full_name as legislator_name
FROM master_votes mv
JOIN master_bills mb ON mv.bill_id = mb.id
LEFT JOIN master_legislators ml ON mv.legislator_id = ml.id
WHERE mv.vote_date >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT 
    'social_post' as activity_type,
    sm.id as subject_id,
    LEFT(sm.content, 100) as subject_title,
    sm.posted_at::date as activity_date,
    sm.content as activity_description,
    ml.state as jurisdiction,
    sm.legislator_id,
    ml.full_name as legislator_name
FROM master_social_media_posts sm
JOIN master_legislators ml ON sm.legislator_id = ml.id
WHERE sm.posted_at >= CURRENT_DATE - INTERVAL '30 days'

ORDER BY activity_date DESC;

-- View for discrepancy reports with detailed information
CREATE OR REPLACE VIEW discrepancy_reports_detailed AS
SELECT 
    mdr.id,
    mdr.legislator_id,
    ml.full_name as legislator_name,
    ml.party,
    ml.state,
    mdr.bill_id,
    mb.bill_number,
    mb.title as bill_title,
    mdr.vote_position,
    mdr.statement_content,
    mdr.statement_source,
    mdr.discrepancy_type,
    mdr.confidence_score,
    mdr.created_at,
    mdr.updated_at
FROM master_discrepancy_reports mdr
JOIN master_legislators ml ON mdr.legislator_id = ml.id
LEFT JOIN master_bills mb ON mdr.bill_id = mb.id;

-- View for committee information with membership counts
CREATE OR REPLACE VIEW committee_details AS
SELECT 
    mc.id,
    mc.name,
    mc.chamber,
    mc.state,
    mc.jurisdiction,
    COUNT(mcm.id) as member_count,
    COUNT(CASE WHEN mcm.title = 'Chair' THEN 1 END) as chair_count,
    STRING_AGG(
        CASE WHEN mcm.title = 'Chair' THEN ml.full_name END, 
        ', '
    ) as chairs,
    mc.created_at,
    mc.updated_at
FROM master_committees mc
LEFT JOIN master_committee_memberships mcm ON mc.id = mcm.master_committee_id
LEFT JOIN master_legislators ml ON mcm.master_legislator_id = ml.id
GROUP BY mc.id, mc.name, mc.chamber, mc.state, mc.jurisdiction, mc.created_at, mc.updated_at;

-- View for party statistics
CREATE OR REPLACE VIEW party_statistics AS
SELECT 
    party,
    COUNT(*) as legislator_count,
    COUNT(CASE WHEN in_office THEN 1 END) as active_legislators,
    AVG(CASE WHEN mk.score IS NOT NULL THEN mk.score END) as avg_truthfulness,
    AVG(CASE WHEN mk2.score IS NOT NULL THEN mk2.score END) as avg_consistency,
    AVG(CASE WHEN mk3.score IS NOT NULL THEN mk3.score END) as avg_engagement
FROM master_legislators ml
LEFT JOIN master_kpi_scores mk ON ml.id = mk.legislator_id AND mk.metric_name = 'truthfulness'
LEFT JOIN master_kpi_scores mk2 ON ml.id = mk2.legislator_id AND mk2.metric_name = 'consistency'
LEFT JOIN master_kpi_scores mk3 ON ml.id = mk3.legislator_id AND mk3.metric_name = 'engagement'
WHERE party IS NOT NULL
GROUP BY party;

-- View for state statistics
CREATE OR REPLACE VIEW state_statistics AS
SELECT 
    state,
    COUNT(*) as legislator_count,
    COUNT(CASE WHEN in_office THEN 1 END) as active_legislators,
    COUNT(DISTINCT chamber) as chamber_count,
    AVG(CASE WHEN mk.score IS NOT NULL THEN mk.score END) as avg_truthfulness,
    AVG(CASE WHEN mk2.score IS NOT NULL THEN mk2.score END) as avg_consistency,
    AVG(CASE WHEN mk3.score IS NOT NULL THEN mk3.score END) as avg_engagement
FROM master_legislators ml
LEFT JOIN master_kpi_scores mk ON ml.id = mk.legislator_id AND mk.metric_name = 'truthfulness'
LEFT JOIN master_kpi_scores mk2 ON ml.id = mk2.legislator_id AND mk2.metric_name = 'consistency'
LEFT JOIN master_kpi_scores mk3 ON ml.id = mk3.legislator_id AND mk3.metric_name = 'engagement'
WHERE state IS NOT NULL
GROUP BY state;