

const uploadForm =
    document.getElementById("uploadForm");

const resumeFile =
    document.getElementById("resumeFile");

const uploadMessage =
    document.getElementById("uploadMessage");

const resumeList =
    document.getElementById("resumeList");

const refreshResumes =
    document.getElementById("refreshResumes");

const analysisSection =
    document.getElementById("analysisSection");

const analysisResult =
    document.getElementById("analysisResult");

const logoutButton =
    document.getElementById("logoutButton");

const jobSeekerDashboard =
    document.getElementById("jobSeekerDashboard");

const employerDashboard =
    document.getElementById("employerDashboard");

const dashboardTitle =
    document.getElementById("dashboardTitle");

const dashboardDescription =
    document.getElementById("dashboardDescription");


/* =========================================================
   GLOBAL DATA
========================================================= */

window.currentResumeId = null;

window.currentAnalysis = null;

window.currentJobRecommendations = [];

window.dashboardStats = {
    resumeScore: 0,
    detectedSkills: 0,
    jobMatches: 0,
    missingSkills: 0,
    missingSkillsList: []
};


/* =========================================================
   LOCAL STORAGE KEYS
========================================================= */

const DASHBOARD_STATS_KEY =
    "ai_resume_dashboard_stats";

const ANALYSIS_DATA_KEY =
    "ai_resume_analysis_data";

const CURRENT_RESUME_KEY =
    "ai_resume_current_resume_id";


/* =========================================================
   SAFE NUMBER
========================================================= */

function safeNumber(value, fallback = 0) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return fallback;
    }

    const number = Number(value);

    return Number.isFinite(number)
        ? number
        : fallback;
}


/* =========================================================
   SAVE CURRENT RESUME
========================================================= */

function saveCurrentResumeId(resumeId) {

    if (!resumeId) {
        return;
    }

    try {

        window.currentResumeId =
            Number(resumeId);

        localStorage.setItem(
            CURRENT_RESUME_KEY,
            String(resumeId)
        );

    } catch (error) {

        console.error(
            "Failed to save current resume:",
            error
        );
    }
}


/* =========================================================
   LOAD CURRENT RESUME
========================================================= */

function loadCurrentResumeId() {

    try {

        const saved =
            localStorage.getItem(
                CURRENT_RESUME_KEY
            );

        if (saved) {

            window.currentResumeId =
                Number(saved);

            return Number(saved);
        }

    } catch (error) {

        console.error(
            "Failed to load current resume:",
            error
        );
    }

    return null;
}


/* =========================================================
   SAVE DASHBOARD STATS
========================================================= */

function saveDashboardStats(
    resumeId,
    stats
) {

    if (!resumeId) {
        return;
    }

    try {

        const allStats =
            JSON.parse(
                localStorage.getItem(
                    DASHBOARD_STATS_KEY
                ) || "{}"
            );

        allStats[String(resumeId)] = {

            resumeScore:
                safeNumber(
                    stats.resumeScore
                ),

            detectedSkills:
                safeNumber(
                    stats.detectedSkills
                ),

            jobMatches:
                safeNumber(
                    stats.jobMatches
                ),

            missingSkills:
                safeNumber(
                    stats.missingSkills
                ),

            missingSkillsList:
                Array.isArray(
                    stats.missingSkillsList
                )
                    ? stats.missingSkillsList
                    : [],

            updatedAt:
                Date.now()
        };

        localStorage.setItem(
            DASHBOARD_STATS_KEY,
            JSON.stringify(allStats)
        );

    } catch (error) {

        console.error(
            "Failed to save dashboard stats:",
            error
        );
    }
}


/* =========================================================
   LOAD DASHBOARD STATS
========================================================= */

function loadSavedDashboardStats(
    resumeId
) {

    if (!resumeId) {
        return null;
    }

    try {

        const allStats =
            JSON.parse(
                localStorage.getItem(
                    DASHBOARD_STATS_KEY
                ) || "{}"
            );

        return (
            allStats[String(resumeId)] ||
            null
        );

    } catch (error) {

        console.error(
            "Failed to load dashboard stats:",
            error
        );

        return null;
    }
}


/* =========================================================
   SAVE ANALYSIS
========================================================= */

function saveAnalysisData(
    resumeId,
    analysis
) {

    if (
        !resumeId ||
        !analysis
    ) {
        return;
    }

    try {

        const allAnalysis =
            JSON.parse(
                localStorage.getItem(
                    ANALYSIS_DATA_KEY
                ) || "{}"
            );

        allAnalysis[String(resumeId)] =
            analysis;

        localStorage.setItem(
            ANALYSIS_DATA_KEY,
            JSON.stringify(allAnalysis)
        );

    } catch (error) {

        console.error(
            "Failed to save analysis:",
            error
        );
    }
}


/* =========================================================
   LOAD SAVED ANALYSIS
========================================================= */

function loadSavedAnalysis(
    resumeId
) {

    if (!resumeId) {
        return null;
    }

    try {

        const allAnalysis =
            JSON.parse(
                localStorage.getItem(
                    ANALYSIS_DATA_KEY
                ) || "{}"
            );

        return (
            allAnalysis[String(resumeId)] ||
            null
        );

    } catch (error) {

        console.error(
            "Failed to load saved analysis:",
            error
        );

        return null;
    }
}


/* =========================================================
   SET ELEMENT TEXT
========================================================= */

function setElementText(
    ids,
    value
) {

    for (const id of ids) {

        const element =
            document.getElementById(id);

        if (element) {

            element.textContent =
                value;
        }
    }
}


/* =========================================================
   UPDATE ALL SCORE ELEMENTS
========================================================= */

function updateScoreElements(score) {

    const formattedScore =
        String(
            safeNumber(score)
        );

    setElementText(
        [
            "resumeScore",
            "resume-score",
            "resumeScoreValue",
            "scoreValue",
            "resumeScoreNumber"
        ],
        formattedScore
    );

    setElementText(
        [
            "scoreCircleValue",
            "largeResumeScore",
            "analysisScore",
            "resumeAnalysisScore",
            "resumeScoreDisplay"
        ],
        formattedScore
    );

    setElementText(
        [
            "resumeScoreTotal",
            "resume-score-total",
            "scoreTotal"
        ],
        "/ 100"
    );
}


/* =========================================================
   UPDATE DASHBOARD STATS
========================================================= */

function updateDashboardStats(
    analysis = {},
    jobData = {},
    resumeId = null
) {

    let skills = [];

    if (
        Array.isArray(
            analysis.skills
        )
    ) {

        skills =
            analysis.skills;

    } else if (
        Array.isArray(
            analysis.detected_skills
        )
    ) {

        skills =
            analysis.detected_skills;

    } else if (
        Array.isArray(
            analysis.detectedSkills
        )
    ) {

        skills =
            analysis.detectedSkills;
    }


    let recommendations = [];

    if (
        Array.isArray(
            jobData.recommendations
        )
    ) {

        recommendations =
            jobData.recommendations;

    } else if (
        Array.isArray(
            jobData.jobs
        )
    ) {

        recommendations =
            jobData.jobs;
    }


    let score = null;

    const possibleScores = [

        analysis.resume_score,
        analysis.resumeScore,
        analysis.score,
        analysis.total_score,
        analysis.totalScore

    ];


    for (
        const possibleScore
        of possibleScores
    ) {

        if (
            possibleScore !== null &&
            possibleScore !== undefined &&
            possibleScore !== ""
        ) {

            score =
                safeNumber(
                    possibleScore,
                    null
                );

            break;
        }
    }


    if (
        score === null ||
        !Number.isFinite(score)
    ) {

        let calculatedScore = 0;

        const skillScore =
            Math.min(
                skills.length * 3,
                40
            );


        let experienceScore = 0;

        if (
            analysis.experience !== null &&
            analysis.experience !== undefined
        ) {

            const experience =
                Array.isArray(
                    analysis.experience
                )
                    ? analysis.experience.join(" ")
                    : String(
                        analysis.experience
                    );

            if (
                experience.trim().length > 20
            ) {

                experienceScore = 25;
            }
        }


        let educationScore = 0;

        if (
            analysis.education !== null &&
            analysis.education !== undefined
        ) {

            const education =
                Array.isArray(
                    analysis.education
                )
                    ? analysis.education.join(" ")
                    : String(
                        analysis.education
                    );

            if (
                education.trim().length > 20
            ) {

                educationScore = 20;
            }
        }


        let summaryScore = 0;

        if (
            analysis.summary !== null &&
            analysis.summary !== undefined
        ) {

            const summary =
                String(
                    analysis.summary
                );

            if (
                summary.trim().length > 20
            ) {

                summaryScore = 15;
            }
        }


        calculatedScore =
            skillScore +
            experienceScore +
            educationScore +
            summaryScore;

        score =
            Math.min(
                Math.round(
                    calculatedScore
                ),
                100
            );
    }


    score =
        Math.max(
            0,
            Math.min(
                100,
                Math.round(score)
            )
        );


    const missingSkills =
        new Set();


    recommendations.forEach(
        job => {

            const missing =
                Array.isArray(
                    job.missing_skills
                )
                    ? job.missing_skills
                    : (
                        Array.isArray(
                            job.missingSkills
                        )
                            ? job.missingSkills
                            : []
                    );


            missing.forEach(
                skill => {

                    if (
                        skill !== null &&
                        skill !== undefined &&
                        String(skill).trim()
                    ) {

                        missingSkills.add(
                            String(skill).trim()
                        );
                    }
                }
            );

        }
    );


    const stats = {

        resumeScore:
            score,

        detectedSkills:
            skills.length,

        jobMatches:
            recommendations.length,

        missingSkills:
            missingSkills.size,

        missingSkillsList:
            Array.from(
                missingSkills
            )
    };


    window.dashboardStats =
        stats;


    if (resumeId) {

        saveDashboardStats(
            resumeId,
            stats
        );
    }


    updateScoreElements(
        stats.resumeScore
    );


    setElementText(
        [
            "detectedSkills",
            "detected-skills",
            "detectedSkillsValue",
            "skillsCount"
        ],
        String(
            stats.detectedSkills
        )
    );


    setElementText(
        [
            "jobMatches",
            "job-matches",
            "jobMatchesValue",
            "matchesCount"
        ],
        String(
            stats.jobMatches
        )
    );


    setElementText(
        [
            "missingSkills",
            "missing-skills",
            "missingSkillsValue",
            "missingCount",
            "missingSkillsCount"
        ],
        String(
            stats.missingSkills
        )
    );


    return stats;
}


/* =========================================================
   RESTORE DASHBOARD STATS
========================================================= */

function restoreDashboardStats(
    resumeId
) {

    const saved =
        loadSavedDashboardStats(
            resumeId
        );


    if (!saved) {
        return;
    }


    window.dashboardStats =
        saved;


    updateScoreElements(
        saved.resumeScore
    );


    setElementText(
        [
            "detectedSkills",
            "detected-skills",
            "detectedSkillsValue",
            "skillsCount"
        ],
        String(
            safeNumber(
                saved.detectedSkills
            )
        )
    );


    setElementText(
        [
            "jobMatches",
            "job-matches",
            "jobMatchesValue",
            "matchesCount"
        ],
        String(
            safeNumber(
                saved.jobMatches
            )
        )
    );


    setElementText(
        [
            "missingSkills",
            "missing-skills",
            "missingSkillsValue",
            "missingCount",
            "missingSkillsCount"
        ],
        String(
            safeNumber(
                saved.missingSkills
            )
        )
    );
}


/* =========================================================
   RESTORE LAST DASHBOARD
========================================================= */

function restoreLastDashboardStats() {

    try {

        const allStats =
            JSON.parse(
                localStorage.getItem(
                    DASHBOARD_STATS_KEY
                ) || "{}"
            );


        const entries =
            Object.entries(
                allStats
            );


        if (
            entries.length === 0
        ) {
            return;
        }


        entries.sort(
            (a, b) =>
                Number(
                    b[1].updatedAt || 0
                ) -
                Number(
                    a[1].updatedAt || 0
                )
        );


        const latest =
            entries[0];

        const resumeId =
            latest[0];

        const stats =
            latest[1];


        saveCurrentResumeId(
            resumeId
        );


        window.dashboardStats =
            stats;


        restoreDashboardStats(
            resumeId
        );

    } catch (error) {

        console.error(
            "Failed to restore latest stats:",
            error
        );
    }
}


/* =========================================================
   LOAD DASHBOARD BY ROLE
========================================================= */

async function loadDashboardByRole() {

    restoreLastDashboardStats();

    try {

        const user =
            await apiRequest(
                "/me"
            );


        if (
            user.role === "employer"
        ) {

            if (jobSeekerDashboard) {
                jobSeekerDashboard.style.display =
                    "none";
            }

            if (employerDashboard) {
                employerDashboard.style.display =
                    "block";
            }

            if (dashboardTitle) {
                dashboardTitle.textContent =
                    "Employer Dashboard";
            }

            if (dashboardDescription) {
                dashboardDescription.textContent =
                    "Create and manage your job opportunities.";
            }

            await loadJobs();

            return;
        }


        if (jobSeekerDashboard) {
            jobSeekerDashboard.style.display =
                "block";
        }

        if (employerDashboard) {
            employerDashboard.style.display =
                "none";
        }

        if (dashboardTitle) {
            dashboardTitle.textContent =
                "Resume Dashboard";
        }

        if (dashboardDescription) {
            dashboardDescription.textContent =
                "Upload your resume and let AI analyze your skills, experience and education.";
        }


        await loadResumes();


        const resumeId =
            loadCurrentResumeId();


        if (resumeId) {

            const savedAnalysis =
                loadSavedAnalysis(
                    resumeId
                );


            if (savedAnalysis) {

                window.currentResumeId =
                    Number(resumeId);

                window.currentAnalysis =
                    savedAnalysis;


                displayAnalysis(
                    savedAnalysis
                );


                if (analysisSection) {
                    analysisSection.style.display =
                        "block";
                }


                await loadJobRecommendations(
                    resumeId
                );


                await loadCareerAdvisor(
                    resumeId
                );


                setupRoadmap(
                    resumeId
                );
            }
        }

    } catch (error) {

        console.error(
            "Dashboard role error:",
            error
        );

        window.location.href =
            "login.html";
    }
}


/* =========================================================
   LOAD RESUMES
========================================================= */

async function loadResumes() {

    if (!resumeList) {
        return;
    }


    resumeList.innerHTML =
        "<p>Loading resumes...</p>";


    try {

        const resumes =
            await apiRequest(
                "/resumes/"
            );


        if (
            !resumes ||
            resumes.length === 0
        ) {

            resumeList.innerHTML =
                "<p>No resumes uploaded yet.</p>";

            return;
        }


        resumeList.innerHTML =
            "";


        resumes.forEach(
            resume => {

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "resume-item";


                card.innerHTML = `

                    <div>

                        <strong>
                            Resume #${resume.id}
                        </strong>

                        <p>
                            ${
                                escapeHtml(
                                    resume.resume_file ||
                                    resume.filename ||
                                    "Uploaded resume"
                                )
                            }
                        </p>

                    </div>


                    <button
                        type="button"
                        class="btn btn-primary analyze-button"
                        data-id="${resume.id}">

                        Analyze

                    </button>

                `;


                resumeList.appendChild(
                    card
                );


                if (
                    Number(
                        window.currentResumeId
                    ) ===
                    Number(
                        resume.id
                    )
                ) {

                    restoreDashboardStats(
                        resume.id
                    );
                }

            }
        );


        document
            .querySelectorAll(
                ".analyze-button"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        () => {

                            const resumeId =
                                Number(
                                    button.dataset.id
                                );


                            analyzeResume(
                                resumeId
                            );
                        }
                    );
                }
            );


    } catch (error) {

        console.error(
            "Load resumes error:",
            error
        );


        resumeList.innerHTML = `

            <p>
                ${
                    escapeHtml(
                        error.message ||
                        "Failed to load resumes."
                    )
                }
            </p>

        `;
    }
}


/* =========================================================
   UPLOAD RESUME
========================================================= */

if (uploadForm) {

    uploadForm.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const file =
                resumeFile.files[0];


            if (!file) {

                uploadMessage.textContent =
                    "Please select a resume.";

                return;
            }


            const allowedTypes = [

                "application/pdf",

                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            ];


            const extension =
                file.name
                    .toLowerCase()
                    .split(".")
                    .pop();


            if (
                !allowedTypes.includes(
                    file.type
                ) &&
                !["pdf", "docx"].includes(
                    extension
                )
            ) {

                uploadMessage.textContent =
                    "Please upload a PDF or DOCX file.";

                return;
            }


            uploadMessage.textContent =
                "Uploading resume...";


            const formData =
                new FormData();


            formData.append(
                "file",
                file
            );


            try {

                const result =
                    await apiRequest(
                        "/resumes/upload",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                console.log(
                    "Upload response:",
                    result
                );


                uploadMessage.textContent =
                    "Resume uploaded successfully!";


                resumeFile.value =
                    "";


                await loadResumes();


            } catch (error) {

                console.error(
                    "Upload error:",
                    error
                );


                uploadMessage.textContent =
                    error.message ||
                    "Upload failed.";
            }

        }
    );
}


/* =========================================================
   ANALYZE RESUME
========================================================= */

async function analyzeResume(
    resumeId
) {

    resumeId =
        Number(resumeId);


    if (!resumeId) {
        return;
    }


    saveCurrentResumeId(
        resumeId
    );


    restoreDashboardStats(
        resumeId
    );


    if (analysisSection) {

        analysisSection.style.display =
            "block";
    }


    if (analysisResult) {

        analysisResult.innerHTML = `

            <div class="analysis-box">

                <p>
                    AI is analyzing your resume...
                </p>

            </div>

        `;
    }


    try {

        const result =
            await apiRequest(
                `/resumes/${resumeId}/analyze`,
                {
                    method: "POST",
                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        if (
            !result ||
            typeof result !== "object"
        ) {

            throw new Error(
                "Invalid analysis response from server."
            );
        }


        window.currentAnalysis =
            result;


        saveAnalysisData(
            resumeId,
            result
        );


        displayAnalysis(
            result
        );


        updateDashboardStats(
            result,
            {},
            resumeId
        );


        await loadJobRecommendations(
            resumeId
        );


        await loadCareerAdvisor(
            resumeId
        );


        setupRoadmap(
            resumeId
        );


    } catch (error) {

        console.error(
            "Resume analysis error:",
            error
        );


        if (analysisResult) {

            analysisResult.innerHTML = `

                <div class="analysis-box">

                    <h3>
                        Analysis Error
                    </h3>

                    <p>
                        ${
                            escapeHtml(
                                error.message ||
                                "Failed to analyze resume."
                            )
                        }
                    </p>

                </div>

            `;
        }
    }
}


/* =========================================================
   DISPLAY ANALYSIS
========================================================= */

function displayAnalysis(
    data
) {

    if (!analysisResult) {
        return;
    }


    const skills =
        Array.isArray(
            data.skills
        )
            ? data.skills
            : (
                Array.isArray(
                    data.detected_skills
                )
                    ? data.detected_skills
                    : (
                        Array.isArray(
                            data.detectedSkills
                        )
                            ? data.detectedSkills
                            : []
                    )
            );


    let score =
        data.resume_score ??
        data.resumeScore ??
        data.score ??
        data.total_score ??
        data.totalScore;


    if (
        score === undefined ||
        score === null
    ) {

        const tempStats =
            updateDashboardStats(
                data,
                {},
                null
            );


        score =
            tempStats.resumeScore;
    }


    score =
        Math.max(
            0,
            Math.min(
                100,
                Math.round(
                    safeNumber(score)
                )
            )
        );


    updateScoreElements(
        score
    );


    analysisResult.innerHTML = `

        <div class="analysis-box score-analysis-box">

            <h3>
                Resume Score
            </h3>

            <div class="resume-score-big">

                <strong>
                    ${score}
                </strong>

                <span>
                    / 100
                </span>

            </div>

        </div>


        <div class="analysis-box">

            <h3>
                Resume Summary
            </h3>

            <p>
                ${formatValue(
                    data.summary
                )}
            </p>

        </div>


        <div class="analysis-box">

            <h3>
                Detected Skills
            </h3>

            <div class="skills-container">

                ${
                    skills.length > 0

                        ? skills
                            .map(
                                skill => `

                                    <span
                                        class="skill-tag">

                                        ${escapeHtml(
                                            skill
                                        )}

                                    </span>

                                `
                            )
                            .join("")

                        : "<p>No skills detected.</p>"
                }

            </div>

        </div>


        <div class="analysis-box">

            <h3>
                Professional Experience
            </h3>

            <p>
                ${formatValue(
                    data.experience
                )}
            </p>

        </div>


        <div class="analysis-box">

            <h3>
                Education
            </h3>

            <p>
                ${formatValue(
                    data.education
                )}
            </p>

        </div>

    `;
}


/* =========================================================
   JOB RECOMMENDATIONS
========================================================= */

async function loadJobRecommendations(
    resumeId
) {

    resumeId =
        Number(resumeId);


    const section =
        document.getElementById(
            "jobRecommendationsSection"
        );


    const resultElement =
        document.getElementById(
            "jobRecommendationsResult"
        );


    if (
        !section ||
        !resultElement
    ) {
        return {
            recommendations: []
        };
    }


    section.style.display =
        "block";


    resultElement.style.display =
        "block";


    resultElement.innerHTML = `

        <div class="analysis-box">

            <p>
                Finding the best jobs for your resume...
            </p>

        </div>

    `;


    try {

        const data =
            await apiRequest(
                `/job-matching/resume/${resumeId}`,
                {
                    method: "POST",
                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        const recommendations =
            Array.isArray(
                data?.recommendations
            )
                ? data.recommendations
                : (
                    Array.isArray(
                        data?.jobs
                    )
                        ? data.jobs
                        : []
                );


        window.currentJobRecommendations =
            recommendations;


        if (
            recommendations.length === 0
        ) {

            resultElement.innerHTML = `

                <div class="analysis-box">

                    <h3>
                        Job Matches
                    </h3>

                    <p>
                        No job recommendations available yet.
                    </p>

                    <p>
                        Ask an employer to add jobs first.
                    </p>

                </div>

            `;


            if (
                window.currentAnalysis
            ) {

                const currentStats =
                    window.dashboardStats || {};


                const preservedStats = {

                    ...currentStats,

                    jobMatches: 0
                };


                window.dashboardStats =
                    preservedStats;


                saveDashboardStats(
                    resumeId,
                    preservedStats
                );


                updateScoreElements(
                    preservedStats.resumeScore
                );


                setElementText(
                    [
                        "skillsCount",
                        "detectedSkills"
                    ],
                    String(
                        preservedStats.detectedSkills || 0
                    )
                );


                setElementText(
                    [
                        "matchesCount",
                        "jobMatches"
                    ],
                    "0"
                );


                setElementText(
                    [
                        "missingSkillsCount",
                        "missingSkills",
                        "missingCount"
                    ],
                    String(
                        preservedStats.missingSkills || 0
                    )
                );
            }


            return {
                ...data,
                recommendations: []
            };
        }


        resultElement.innerHTML =
            recommendations
                .map(
                    (job, index) => {

                        const matchScore =
                            job.score ??
                            job.match_score ??
                            job.matchScore ??
                            0;


                        const matchedSkills =
                            job.matched_skills ??
                            job.matchedSkills ??
                            [];


                        const missingSkills =
                            job.missing_skills ??
                            job.missingSkills ??
                            [];


                        return `

                            <div
                                class="analysis-box job-card">

                                <h3>

                                    ${escapeHtml(
                                        job.title ||
                                        job.job_title ||
                                        `Job Opportunity ${index + 1}`
                                    )}

                                </h3>


                                <p>

                                    <strong>
                                        Match Score:
                                    </strong>

                                    <span
                                        class="match-score">

                                        ${safeNumber(
                                            matchScore
                                        )}%

                                    </span>

                                </p>


                                <p>

                                    <strong>
                                        Matched Skills:
                                    </strong>

                                    ${formatValue(
                                        matchedSkills
                                    )}

                                </p>


                                <p>

                                    <strong>
                                        Missing Skills:
                                    </strong>

                                    ${formatValue(
                                        missingSkills
                                    )}

                                </p>


                                <p>

                                    <strong>
                                        Why this job:
                                    </strong>

                                    ${formatValue(
                                        job.reason ||
                                        job.explanation ||
                                        job.description
                                    )}

                                </p>

                            </div>

                        `;
                    }
                )
                .join("");


        if (
            window.currentAnalysis
        ) {

            updateDashboardStats(
                window.currentAnalysis,
                {
                    recommendations:
                        recommendations
                },
                resumeId
            );
        }


        return {
            ...data,
            recommendations
        };


    } catch (error) {

        console.error(
            "JOB MATCHING ERROR:",
            error
        );


        resultElement.innerHTML = `

            <div class="analysis-box">

                <h3>
                    Job Matching
                </h3>

                <p>
                    Job matching could not be completed.
                </p>

                <p>
                    ${
                        escapeHtml(
                            error.message ||
                            "Unknown error"
                        )
                    }
                </p>

            </div>

        `;


        if (window.dashboardStats) {

            updateScoreElements(
                window.dashboardStats.resumeScore
            );


            setElementText(
                [
                    "skillsCount",
                    "detectedSkills"
                ],
                String(
                    window.dashboardStats.detectedSkills || 0
                )
            );


            setElementText(
                [
                    "matchesCount",
                    "jobMatches"
                ],
                String(
                    window.dashboardStats.jobMatches || 0
                )
            );


            setElementText(
                [
                    "missingSkillsCount",
                    "missingSkills",
                    "missingCount"
                ],
                String(
                    window.dashboardStats.missingSkills || 0
                )
            );
        }


        return {
            recommendations: [],
            error: true
        };
    }
}


/* =========================================================
   CAREER ADVISOR
========================================================= */

async function loadCareerAdvisor(
    resumeId
) {

    resumeId =
        Number(resumeId);


    const section =
        document.getElementById(
            "careerAdvisorSection"
        );


    const resultElement =
        document.getElementById(
            "careerAdvisorResult"
        );


    const button =
        document.getElementById(
            "askCareerButton"
        );


    const input =
        document.getElementById(
            "careerQuestion"
        );


    if (
        !section ||
        !resultElement ||
        !button ||
        !input
    ) {
        return;
    }


    section.style.display =
        "block";


    resultElement.style.display =
        "block";


    resultElement.innerHTML = `

        <p>
            Career Advisor is ready.
            Ask a question about your career.
        </p>

    `;


    button.onclick =
        null;


    button.onclick =
        async () => {

            const question =
                input.value.trim();


            if (!question) {

                resultElement.style.display =
                    "block";


                resultElement.innerHTML = `

                    <div class="analysis-box">

                        <p>
                            Please enter a question.
                        </p>

                    </div>

                `;

                return;
            }


            resultElement.innerHTML = `

                <div class="analysis-box">

                    <p>
                        Career Advisor is thinking...
                    </p>

                </div>

            `;


            button.disabled =
                true;


            try {

                const data =
                    await apiRequest(
                        "/career-advisor/ask",
                        {
                            method: "POST",

                            headers: {

                                "Accept":
                                    "application/json",

                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    resume_id:
                                        Number(
                                            resumeId
                                        ),

                                    question:
                                        question
                                })
                        }
                    );


                resultElement.innerHTML = `

                    <div class="analysis-box">

                        <h3>
                            Career Advice
                        </h3>

                        <p>
                            ${formatValue(
                                data.answer ??
                                data.response ??
                                data.advice ??
                                data.message
                            )}
                        </p>

                    </div>


                    <div class="analysis-box">

                        <strong>
                            Your Skills:
                        </strong>

                        <p>
                            ${formatValue(
                                data.user_skills ??
                                data.userSkills
                            )}
                        </p>

                    </div>


                    <div class="analysis-box">

                        <strong>
                            Matched Skills:
                        </strong>

                        <p>
                            ${formatValue(
                                data.matched_skills ??
                                data.matchedSkills
                            )}
                        </p>

                    </div>


                    <div class="analysis-box">

                        <strong>
                            Missing Skills:
                        </strong>

                        <p>
                            ${formatValue(
                                data.missing_skills ??
                                data.missingSkills
                            )}
                        </p>

                    </div>

                `;


            } catch (error) {

                console.error(
                    "CAREER ADVISOR ERROR:",
                    error
                );


                resultElement.innerHTML = `

                    <div class="analysis-box">

                        <h3>
                            Career Advisor Error
                        </h3>

                        <p>
                            ${
                                escapeHtml(
                                    error.message ||
                                    "Failed to get career advice."
                                )
                            }
                        </p>

                    </div>

                `;

            } finally {

                button.disabled =
                    false;
            }
        };
}


/* =========================================================
   ROADMAP SETUP
========================================================= */

function setupRoadmap(
    resumeId
) {

    resumeId =
        Number(resumeId);


    const section =
        document.getElementById(
            "roadmapSection"
        );


    const button =
        document.getElementById(
            "generateRoadmapButton"
        );


    if (
        !section ||
        !button
    ) {

        console.error(
            "Roadmap HTML elements are missing."
        );

        return;
    }


    section.style.display =
        "block";


    button.dataset.resumeId =
        String(resumeId);
}


/* =========================================================
   CREATE VISUAL ROADMAP STEPS
========================================================= */

function createRoadmapSteps(
    roadmapData
) {

    let steps = [];

    if (
        roadmapData &&
        typeof roadmapData === "object" &&
        !Array.isArray(roadmapData) &&
        Array.isArray(roadmapData.steps)
    ) {
        steps = roadmapData.steps;
    } else if (Array.isArray(roadmapData)) {
        steps = roadmapData;
    }

    if (steps.length > 0) {
        return steps
            .map((step, index) => {
                const topics = Array.isArray(step.topics) ? step.topics : [];
                const projects = Array.isArray(step.projects) ? step.projects : [];
                const resources = Array.isArray(step.resources) ? step.resources : [];
                const details = [...topics, ...projects, ...resources];
                const detailLabel = projects.length > 0
                    ? "Practice project"
                    : resources.length > 0
                        ? "Suggested resource"
                        : "Focus areas";

                return `
                    <article class="roadmap-step ${index === 0 ? "is-open" : ""}" data-roadmap-step="${index}">
                        <div class="roadmap-step-marker">${index + 1}</div>
                        <div class="roadmap-step-card">
                            <button type="button" class="roadmap-step-toggle" aria-expanded="${index === 0 ? "true" : "false"}">
                                <span class="roadmap-step-heading">
                                    <span class="roadmap-step-kicker">Stage ${index + 1} ${escapeHtml(step.level || "Learning")}</span>
                                    <strong>${escapeHtml(step.title || step.skill || `Learning Stage ${index + 1}`)}</strong>
                                </span>
                                <span class="roadmap-step-meta">
                                    ${step.duration ? `<span class="roadmap-duration">◷ ${escapeHtml(step.duration)}</span>` : ""}
                                    <span class="roadmap-chevron">⌄</span>
                                </span>
                            </button>
                            <div class="roadmap-step-details">
                                <p class="roadmap-step-description">${escapeHtml(step.description || `Build practical knowledge in ${step.skill || "this skill"}.`)}</p>
                                ${step.skill ? `<div class="roadmap-focus"><span>Skill gap</span><strong>${escapeHtml(step.skill)}</strong></div>` : ""}
                                ${details.length > 0 ? `<div class="roadmap-detail-grid"><div><span class="roadmap-detail-label">${detailLabel}</span><ul>${details.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div></div>` : ""}
                                <label class="roadmap-complete"><input type="checkbox" class="roadmap-complete-checkbox"><span>Mark this stage complete</span></label>
                            </div>
                        </div>
                    </article>
                    ${index < steps.length - 1 ? `<div class="roadmap-connector" aria-hidden="true"><span>↓</span></div>` : ""}
                `;
            })
            .join("");
    }

    let text = "";


    if (
        typeof roadmapData ===
        "string"
    ) {

        text =
            roadmapData;

    } else if (
        Array.isArray(
            roadmapData
        )
    ) {

        text =
            roadmapData.join("\n");

    } else if (roadmapData && typeof roadmapData === "object") {
        text = roadmapData.description || roadmapData.goal || "";
    }


    text =
        String(text || "")
            .replace(/\r/g, "")
            .trim();


    if (!text) {

        return `

            <div class="roadmap-step">

                <div class="roadmap-step-number">
                    1
                </div>

                <div class="roadmap-step-content">

                    <h4>
                        Learning Roadmap
                    </h4>

                    <p>
                        No detailed roadmap content
                        was returned by the AI.
                    </p>

                </div>

            </div>

        `;
    }


    /*
     * Detect numbered sections such as:
     *
     * 1. Machine Learning
     * 2. Deep Learning
     * 3. APIs
     */

    let sections =
        text
            .split(
                /\n(?=\s*(?:#{1,4}\s*)?(?:\*\*)?\d+[\.\)]\s*)/
            )
            .map(
                section =>
                    section.trim()
            )
            .filter(Boolean);


    /*
     * If the AI uses markdown headings,
     * split those too.
     */

    if (
        sections.length <= 1 &&
        text.includes("\n###")
    ) {

        sections =
            text
                .split(
                    /\n(?=###\s*)/
                )
                .map(
                    section =>
                        section.trim()
                )
                .filter(Boolean);
    }


    /*
     * If still one section, try common
     * bold numbered headings.
     */

    if (
        sections.length <= 1
    ) {

        const matches =
            text.match(
                /(?:^|\n)\s*(?:\*\*)?\d+[\.\)]\s*[^:\n]+(?::|\*\*)?/g
            );


        if (
            matches &&
            matches.length > 1
        ) {

            sections =
                text
                    .split(
                        /\n(?=\s*(?:\*\*)?\d+[\.\)]\s*)/
                    )
                    .map(
                        section =>
                            section.trim()
                    )
                    .filter(Boolean);
        }
    }


    if (
        sections.length === 0
    ) {

        sections = [text];
    }


    return sections
        .map(
            (section, index) => {

                let cleanSection =
                    section
                        .replace(
                            /^#{1,4}\s*/,
                            ""
                        )
                        .replace(
                            /^\*\*/,
                            ""
                        )
                        .replace(
                            /\*\*$/,
                            ""
                        )
                        .trim();


                const lines =
                    cleanSection
                        .split("\n")
                        .map(
                            line =>
                                line.trim()
                        )
                        .filter(Boolean);


                let title =
                    lines.shift() ||
                    `Learning Step ${index + 1}`;


                title =
                    title
                        .replace(
                            /^#{1,4}\s*/,
                            ""
                        )
                        .replace(
                            /^\*\*/,
                            ""
                        )
                        .replace(
                            /\*\*$/,
                            ""
                        )
                        .replace(
                            /^\d+[\.\)]\s*/,
                            ""
                        )
                        .trim();


                const content =
                    lines
                        .map(
                            line => {

                                const clean =
                                    line
                                        .replace(
                                            /^[-*•]\s*/,
                                            ""
                                        )
                                        .replace(
                                            /^\d+[\.\)]\s*/,
                                            ""
                                        )
                                        .replace(
                                            /\*\*/g,
                                            ""
                                        )
                                        .trim();


                                if (!clean) {
                                    return "";
                                }


                                return `

                                    <li>
                                        ${escapeHtml(
                                            clean
                                        )}
                                    </li>

                                `;
                            }
                        )
                        .filter(Boolean)
                        .join("");


                return `

                    <div class="roadmap-step">

                        <div class="roadmap-step-number">

                            ${index + 1}

                        </div>


                        <div class="roadmap-step-content">

                            <h4>
                                ${escapeHtml(
                                    title
                                )}
                            </h4>


                            ${
                                content
                                    ? `
                                        <ul>
                                            ${content}
                                        </ul>
                                      `
                                    : ""
                            }

                        </div>

                    </div>


                    ${
                        index <
                        sections.length - 1

                            ? `

                                <div class="roadmap-connector">

                                    <span>
                                        ↓
                                    </span>

                                </div>

                              `

                            : ""
                    }

                `;
            }
        )
        .join("");
}


/* =========================================================
   LOAD ROADMAP
   VISUAL NOTEBOOKLM-STYLE PRESENTATION
========================================================= */

async function loadRoadmap(
    resumeId
) {

    resumeId =
        Number(resumeId);


    const section =
        document.getElementById(
            "roadmapSection"
        );


    const resultElement =
        document.getElementById(
            "roadmapResult"
        );


    if (
        !section ||
        !resultElement
    ) {

        console.error(
            "Roadmap elements not found."
        );

        return;
    }


    if (!resumeId) {

        resultElement.style.display =
            "block";


        resultElement.innerHTML = `

            <div class="analysis-box">

                <p>
                    Please analyze a resume first.
                </p>

            </div>

        `;

        resultElement.querySelectorAll(".roadmap-step-toggle").forEach(button => {
            button.addEventListener("click", () => {
                const step = button.closest(".roadmap-step");
                const isOpen = step.classList.toggle("is-open");
                button.setAttribute("aria-expanded", String(isOpen));
            });
        });

        resultElement.querySelectorAll(".roadmap-complete-checkbox").forEach(checkbox => {
            checkbox.addEventListener("change", () => {
                checkbox.closest(".roadmap-step").classList.toggle("is-complete", checkbox.checked);
            });
        });

        return;
    }


    section.style.display =
        "block";


    resultElement.style.display =
        "block";


    resultElement.innerHTML = `

        <div class="analysis-box">

            <p>
                AI is building your personalized career roadmap...
            </p>

        </div>

    `;


    try {

        console.log(
            "Calling Roadmap:",
            resumeId
        );


        const endpoint =
            `/career-advisor/roadmap?resume_id=${encodeURIComponent(
                resumeId
            )}`;


        const data =
            await apiRequest(
                endpoint,
                {
                    method: "POST",

                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        console.log(
            "ROADMAP RESPONSE:",
            data
        );


        const missingSkills =
            data.missing_skills ??
            data.missingSkills ??
            [];


        const roadmap =
            data.steps ??
            data.roadmap ??
            data.learning_roadmap ??
            data.learningRoadmap ??
            "";


        resultElement.style.display =
            "block";


        const title = data.title || "Your Personalized Learning Roadmap";
        const goal = data.goal || "Build the skills you need in the right order.";
        const totalSteps = Array.isArray(roadmap)
            ? roadmap.length
            : safeNumber(data.total_steps);
        const score = safeNumber(window.dashboardStats.resumeScore, 0);

        resultElement.innerHTML = `

            <div class="roadmap-container">

                <div class="roadmap-header">

                    <div>

                        <span class="roadmap-label">

                            AI CAREER GUIDANCE

                        </span>


                        <h2>

                            ${escapeHtml(title)}

                        </h2>


                        <p>

                            ${escapeHtml(goal)}

                        </p>

                    </div>

                </div>


                <div class="roadmap-missing-skills">

                    <h3>

                        Your Skill Gaps

                    </h3>


                    <div class="roadmap-skills">

                        ${
                            Array.isArray(
                                missingSkills
                            ) &&
                            missingSkills.length > 0

                                ? missingSkills
                                    .map(
                                        skill => `

                                            <span
                                                class="roadmap-skill">

                                                ${escapeHtml(
                                                    skill
                                                )}

                                            </span>

                                        `
                                    )
                                    .join("")

                                : `

                                    <span
                                        class="roadmap-skill">

                                        Great! No major skill gaps were detected.

                                    </span>

                                  `
                        }

                    </div>

                </div>


                <div class="roadmap-path">

                    ${createRoadmapSteps(
                        roadmap
                    )}

                </div>

                <div class="roadmap-progress" aria-live="polite">
                    <span><strong class="roadmap-completed-count">0</strong> of ${totalSteps} steps complete</span>
                    ${score ? `<span>Resume score: <strong>${score}/100</strong></span>` : ""}
                    <div class="roadmap-progress-track"><span style="width: 0%"></span></div>
                </div>


                <div class="roadmap-footer">

                    <span>

                        Select a stage to inspect its topics and mark progress as you learn.

                    </span>

                </div>

            </div>

        `;

        const updateRoadmapProgress = () => {
            const checkboxes = [...resultElement.querySelectorAll(".roadmap-complete-checkbox")];
            const completed = checkboxes.filter(checkbox => checkbox.checked).length;
            const percentage = checkboxes.length
                ? Math.round((completed / checkboxes.length) * 100)
                : 0;
            const count = resultElement.querySelector(".roadmap-completed-count");
            const progress = resultElement.querySelector(".roadmap-progress-track span");

            if (count) count.textContent = String(completed);
            if (progress) progress.style.width = `${percentage}%`;
        };

        resultElement.querySelectorAll(".roadmap-step-toggle").forEach(button => {
            button.addEventListener("click", () => {
                const step = button.closest(".roadmap-step");
                const isOpen = step.classList.toggle("is-open");
                button.setAttribute("aria-expanded", String(isOpen));
            });
        });

        resultElement.querySelectorAll(".roadmap-complete-checkbox").forEach(checkbox => {
            checkbox.addEventListener("change", () => {
                checkbox.closest(".roadmap-step").classList.toggle("is-complete", checkbox.checked);
                updateRoadmapProgress();
            });
        });


    } catch (error) {

        console.error(
            "ROADMAP ERROR:",
            error
        );


        resultElement.style.display =
            "block";


        resultElement.innerHTML = `

            <div class="analysis-box">

                <h3>
                    Roadmap Error
                </h3>

                <p>

                    ${
                        escapeHtml(
                            error.message ||
                            "Failed to generate roadmap."
                        )
                    }

                </p>

            </div>

        `;
    }
}


/* =========================================================
   ROADMAP BUTTON
========================================================= */

const generateRoadmapButton =
    document.getElementById(
        "generateRoadmapButton"
    );


if (generateRoadmapButton) {

    generateRoadmapButton.addEventListener(
        "click",
        async () => {

            let resumeId =
                Number(
                    generateRoadmapButton.dataset.resumeId
                );


            if (!resumeId) {

                resumeId =
                    Number(
                        window.currentResumeId
                    );
            }


            if (!resumeId) {

                resumeId =
                    Number(
                        loadCurrentResumeId()
                    );
            }


            if (!resumeId) {

                const resultElement =
                    document.getElementById(
                        "roadmapResult"
                    );


                if (resultElement) {

                    resultElement.style.display =
                        "block";


                    resultElement.innerHTML = `

                        <div class="analysis-box">

                            <p>
                                Please analyze a resume first.
                            </p>

                        </div>

                    `;
                }


                return;
            }


            await loadRoadmap(
                resumeId
            );
        }
    );
}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );
}


/* =========================================================
   FORMAT VALUE
========================================================= */

function formatValue(
    value
) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return "Not available";
    }


    if (
        Array.isArray(value)
    ) {

        if (
            value.length === 0
        ) {

            return "None";
        }


        return value
            .map(
                item =>
                    escapeHtml(
                        typeof item === "object"
                            ? JSON.stringify(item)
                            : item
                    )
            )
            .join(", ");
    }


    if (
        typeof value === "object"
    ) {

        return `

            <pre>${escapeHtml(
                JSON.stringify(
                    value,
                    null,
                    2
                )
            )}</pre>

        `;
    }


    return escapeHtml(
        value
    );
}


/* =========================================================
   REFRESH RESUMES
========================================================= */

if (refreshResumes) {

    refreshResumes.addEventListener(
        "click",
        async () => {

            await loadResumes();

        }
    );
}


/* =========================================================
   LOGOUT
========================================================= */

if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        async () => {

            try {

                await apiRequest(
                    "/logout",
                    {
                        method: "POST"
                    }
                );

            } catch (error) {

                console.error(
                    "Logout error:",
                    error
                );
            }


            window.location.href =
                "login.html";
        }
    );
}


/* =========================================================
   EMPLOYER ELEMENTS
========================================================= */

const jobForm =
    document.getElementById(
        "jobForm"
    );

const jobTitle =
    document.getElementById(
        "jobTitle"
    );

const jobContent =
    document.getElementById(
        "jobContent"
    );

const jobSkills =
    document.getElementById(
        "jobSkills"
    );

const jobMessage =
    document.getElementById(
        "jobMessage"
    );

const jobSearch =
    document.getElementById(
        "jobSearch"
    );

const jobList =
    document.getElementById(
        "jobList"
    );

const refreshJobs =
    document.getElementById(
        "refreshJobs"
    );


/* =========================================================
   FORMAT SKILLS
========================================================= */

function formatSkills(
    skills
) {

    if (!skills) {

        return "No skills specified";
    }


    if (
        Array.isArray(skills)
    ) {

        if (
            skills.length === 0
        ) {

            return "No skills specified";
        }


        return skills
            .map(
                skill =>
                    escapeHtml(
                        skill
                    )
            )
            .join(", ");
    }


    return escapeHtml(
        skills
    );
}


/* =========================================================
   RENDER JOBS
========================================================= */

function renderJobs(
    jobs
) {

    if (!jobList) {
        return;
    }


    if (
        !jobs ||
        jobs.length === 0
    ) {

        jobList.innerHTML =
            "<p>No jobs found.</p>";

        return;
    }


    jobList.innerHTML =
        jobs
            .map(
                job => `

                    <div
                        class="resume-item job-item">

                        <div
                            class="job-info">

                            <h3>
                                ${escapeHtml(
                                    job.title ||
                                    "Untitled Job"
                                )}
                            </h3>


                            <p>
                                ${escapeHtml(
                                    job.content ||
                                    ""
                                )}
                            </p>


                            <p>

                                <strong>
                                    Required Skills:
                                </strong>

                                ${formatSkills(
                                    job.required_skills
                                )}

                            </p>


                            <p>

                                <strong>
                                    Job ID:
                                </strong>

                                ${job.id}

                            </p>

                        </div>


                        <div
                            class="job-actions">

                            <button
                                type="button"
                                class="btn btn-secondary edit-job-button"
                                data-id="${job.id}">

                                Edit

                            </button>


                            <button
                                type="button"
                                class="btn btn-danger delete-job-button"
                                data-id="${job.id}">

                                Delete

                            </button>

                        </div>

                    </div>

                `
            )
            .join("");


    document
        .querySelectorAll(
            ".delete-job-button"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () =>
                        deleteJob(
                            button.dataset.id
                        )
                );
            }
        );


    document
        .querySelectorAll(
            ".edit-job-button"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () =>
                        editJob(
                            button.dataset.id
                        )
                );
            }
        );
}


/* =========================================================
   LOAD JOBS
========================================================= */

async function loadJobs(
    keyword = ""
) {

    if (!jobList) {
        return;
    }


    jobList.innerHTML =
        "<p>Loading jobs...</p>";


    try {

        let endpoint =
            "/jobs/";


        if (
            keyword.trim()
        ) {

            endpoint =
                `/jobs/search?keyword=${encodeURIComponent(
                    keyword.trim()
                )}`;
        }


        const jobs =
            await apiRequest(
                endpoint
            );


        renderJobs(
            jobs
        );


    } catch (error) {

        console.error(
            "Load jobs error:",
            error
        );


        jobList.innerHTML =
            `<p>${escapeHtml(
                error.message
            )}</p>`;
    }
}


/* =========================================================
   CREATE JOB
========================================================= */

if (jobForm) {

    jobForm.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const title =
                jobTitle.value.trim();


            const content =
                jobContent.value.trim();


            const skills =
                jobSkills.value
                    .split(",")
                    .map(
                        skill =>
                            skill.trim()
                    )
                    .filter(Boolean);


            if (
                !title ||
                !content
            ) {

                jobMessage.textContent =
                    "Please enter the job title and description.";

                return;
            }


            jobMessage.textContent =
                "Creating job...";


            try {

                const result =
                    await apiRequest(
                        "/jobs/",
                        {
                            method: "POST",

                            headers: {

                                "Accept":
                                    "application/json",

                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    title:
                                        title,

                                    content:
                                        content,

                                    required_skills:
                                        skills
                                })
                        }
                    );


                console.log(
                    "Job created:",
                    result
                );


                jobMessage.textContent =
                    "Job created successfully!";


                jobForm.reset();


                await loadJobs();


            } catch (error) {

                console.error(
                    "Create job error:",
                    error
                );


                jobMessage.textContent =
                    error.message ||
                    "Failed to create job.";
            }
        }
    );
}


/* =========================================================
   DELETE JOB
========================================================= */

async function deleteJob(
    jobId
) {

    if (
        !confirm(
            "Are you sure you want to delete this job?"
        )
    ) {

        return;
    }


    try {

        await apiRequest(
            `/jobs/${jobId}`,
            {
                method: "DELETE"
            }
        );


        await loadJobs();


    } catch (error) {

        console.error(
            "Delete job error:",
            error
        );


        alert(
            error.message
        );
    }
}


/* =========================================================
   EDIT JOB
========================================================= */

async function editJob(
    jobId
) {

    const title =
        prompt(
            "New Job Title:"
        );


    if (
        title === null
    ) {

        return;
    }


    const content =
        prompt(
            "New Job Description:"
        );


    if (
        content === null
    ) {

        return;
    }


    const skillsInput =
        prompt(
            "Required Skills (comma separated):"
        );


    if (
        skillsInput === null
    ) {

        return;
    }


    const skills =
        skillsInput
            .split(",")
            .map(
                skill =>
                    skill.trim()
            )
            .filter(Boolean);


    try {

        await apiRequest(
            `/jobs/${jobId}`,
            {
                method: "PUT",

                headers: {

                    "Accept":
                        "application/json",

                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({

                        title:
                            title.trim(),

                        content:
                            content.trim(),

                        required_skills:
                            skills
                    })
            }
        );


        await loadJobs();


    } catch (error) {

        console.error(
            "Edit job error:",
            error
        );


        alert(
            error.message
        );
    }
}


/* =========================================================
   JOB SEARCH
========================================================= */

if (refreshJobs) {

    refreshJobs.addEventListener(
        "click",
        () =>
            loadJobs()
    );
}


if (jobSearch) {

    jobSearch.addEventListener(
        "input",
        () =>
            loadJobs(
                jobSearch.value
            )
    );
}


/* =========================================================
   START DASHBOARD
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadDashboardByRole();

    }
);