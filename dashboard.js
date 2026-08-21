const uploadForm = document.getElementById("uploadForm");
const resumeFile = document.getElementById("resumeFile");
const uploadMessage = document.getElementById("uploadMessage");
const resumeList = document.getElementById("resumeList");
const refreshResumes = document.getElementById("refreshResumes");
const analysisSection = document.getElementById("analysisSection");
const analysisResult = document.getElementById("analysisResult");
const logoutButton = document.getElementById("logoutButton");
const jobSeekerDashboard = document.getElementById("jobSeekerDashboard");
const employerDashboard = document.getElementById("employerDashboard");
const dashboardTitle = document.getElementById("dashboardTitle");
const dashboardDescription = document.getElementById("dashboardDescription");

async function loadDashboardByRole() {
    try {
        const user = await apiRequest("/me");

        console.log("Current user:", user);

        if (user.role === "employer") {
            if (jobSeekerDashboard) {
                jobSeekerDashboard.style.display = "none";
            }

            if (employerDashboard) {
                employerDashboard.style.display = "block";
            }

            if (dashboardTitle) {
                dashboardTitle.textContent = "Employer Dashboard";
            }

            if (dashboardDescription) {
                dashboardDescription.textContent =
                    "Create and manage your job opportunities.";
            }

            return;
        }

        if (jobSeekerDashboard) {
            jobSeekerDashboard.style.display = "block";
        }

        if (employerDashboard) {
            employerDashboard.style.display = "none";
        }

        if (dashboardTitle) {
            dashboardTitle.textContent = "Resume Dashboard";
        }

        if (dashboardDescription) {
            dashboardDescription.textContent =
                "Upload your resume and let AI analyze your skills, experience and education.";
        }

    } catch (error) {
        console.error("Dashboard role error:", error);

        window.location.href = "login.html";
    }
}
async function loadResumes() {
    resumeList.innerHTML = "<p>Loading resumes...</p>";

    try {
        const resumes = await apiRequest("/resumes/");

        if (!resumes || resumes.length === 0) {
            resumeList.innerHTML = "<p>No resumes uploaded yet.</p>";
            return;
        }

        resumeList.innerHTML = "";

        resumes.forEach(resume => {
            const card = document.createElement("div");
            card.className = "resume-item";

            card.innerHTML = `
                <div>
                    <strong>Resume #${resume.id}</strong>
                    <p>${resume.resume_file || "Uploaded resume"}</p>
                </div>

                <button
                    class="btn btn-primary analyze-button"
                    data-id="${resume.id}">
                    Analyze
                </button>
            `;

            resumeList.appendChild(card);
        });

        document.querySelectorAll(".analyze-button").forEach(button => {
            button.addEventListener("click", () => {
                analyzeResume(button.dataset.id);
            });
        });

    } catch (error) {
        console.error(error);
        resumeList.innerHTML = `<p>${error.message}</p>`;
    }
}

if (uploadForm) {
    uploadForm.addEventListener("submit", async event => {
        event.preventDefault();

        const file = resumeFile.files[0];

        if (!file) {
            uploadMessage.textContent = "Please select a resume.";
            return;
        }

        uploadMessage.textContent = "Uploading resume...";

        const formData = new FormData();
        formData.append("file", file);

        try {
            await apiRequest("/resumes/upload", {
                method: "POST",
                body: formData
            });

            uploadMessage.textContent =
                "Resume uploaded successfully!";

            resumeFile.value = "";

            await loadResumes();

        } catch (error) {
            console.error(error);
            uploadMessage.textContent =
                error.message || "Upload failed.";
        }
    });
}

async function analyzeResume(resumeId) {
    analysisSection.style.display = "block";

    analysisResult.innerHTML =
        "<p>AI is analyzing your resume...</p>";

    try {
        const result = await apiRequest(
            `/resumes/${resumeId}/analyze`,
            {
                method: "POST"
            }
        );

        displayAnalysis(result);

        await loadJobRecommendations(resumeId);
        window.currentResumeId = Number(resumeId);

        const roadmapSection = document.getElementById("roadmapSection");
        if (roadmapSection) roadmapSection.style.display = "block";

        const roadmapButton = document.getElementById("generateRoadmapButton");
        if (roadmapButton) {
            roadmapButton.dataset.resumeId = String(resumeId);
        }

        await loadCareerAdvisor(resumeId);

    } catch (error) {
        console.error(error);

        analysisResult.innerHTML =
            `<p>${error.message}</p>`;
    }
}

function displayAnalysis(data) {
    analysisResult.innerHTML = `
        <div class="analysis-box">
            <h3>Summary</h3>
            <p>${formatValue(data.summary)}</p>
        </div>

        <div class="analysis-box">
            <h3>Skills</h3>
            <p>${formatValue(data.skills)}</p>
        </div>

        <div class="analysis-box">
            <h3>Experience</h3>
            <p>${formatValue(data.experience)}</p>
        </div>

        <div class="analysis-box">
            <h3>Education</h3>
            <p>${formatValue(data.education)}</p>
        </div>
    `;
}

function formatValue(value) {
    if (value === null || value === undefined) {
        return "Not available";
    }

    if (Array.isArray(value)) {
        return value.join(", ");
    }

    if (typeof value === "object") {
        return JSON.stringify(value, null, 2);
    }

    return String(value);
}

async function loadJobRecommendations(resumeId) {
    const section =
        document.getElementById("jobRecommendationsSection");

    const resultElement =
        document.getElementById("jobRecommendationsResult");

    if (!section || !resultElement) return;

    section.style.display = "block";

    resultElement.innerHTML =
        "<p>Finding the best jobs for your resume...</p>";

    try {
        const data = await apiRequest(
            `/job-matching/resume/${resumeId}`,
            {
                method: "POST"
            }
        );

        if (!data.recommendations ||
            data.recommendations.length === 0) {

            resultElement.innerHTML = `
                <p>No job recommendations available yet.</p>
                <p>Ask an employer to add jobs first.</p>
            `;

            return;
        }

        resultElement.innerHTML =
            data.recommendations.map(job => `
                <div class="analysis-box job-card">

                    <h3>${job.title}</h3>

                    <p>
                        <strong>Match Score:</strong>
                        ${job.score}%
                    </p>

                    <p>
                        <strong>Matched Skills:</strong>
                        ${formatValue(job.matched_skills)}
                    </p>

                    <p>
                        <strong>Missing Skills:</strong>
                        ${formatValue(job.missing_skills)}
                    </p>

                    <p>
                        <strong>Why:</strong>
                        ${job.reason}
                    </p>

                </div>
            `).join("");

    } catch (error) {
        console.error("Job recommendations error:", error);

        resultElement.innerHTML =
            `<p>${error.message}</p>`;
    }
}

async function loadCareerAdvisor(resumeId) {
    const section = document.getElementById("careerAdvisorSection");
    const resultElement = document.getElementById("careerAdvisorResult");

    if (!section || !resultElement) return;

    section.style.display = "block";
    resultElement.style.display = "block";

    resultElement.innerHTML = `
        <p>
            Career Advisor is ready.
            Ask a question about your career.
        </p>
    `;

    const button = document.getElementById("askCareerButton");
    const input = document.getElementById("careerQuestion");

    if (!button || !input) return;

    button.onclick = async () => {
        const question = input.value.trim();

        if (!question) {
            resultElement.innerHTML =
                "<p>Please enter a question.</p>";
            return;
        }

        resultElement.innerHTML =
            "<p>Career Advisor is thinking...</p>";

        try {
            const data = await apiRequest(
                "/career-advisor/ask",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        resume_id: Number(resumeId),
                        question: question
                    })
                }
            );

            resultElement.innerHTML = `
                <div class="analysis-box">
                    <h3>Career Advice</h3>
                    <p>${formatValue(data.answer)}</p>
                </div>

                <div class="analysis-box">
                    <strong>Your Skills:</strong>
                    <p>${formatValue(data.user_skills)}</p>
                </div>

                <div class="analysis-box">
                    <strong>Matched Skills:</strong>
                    <p>${formatValue(data.matched_skills)}</p>
                </div>

                <div class="analysis-box">
                    <strong>Missing Skills:</strong>
                    <p>${formatValue(data.missing_skills)}</p>
                </div>
            `;

        } catch (error) {
            console.error("Career Advisor error:", error);

            resultElement.innerHTML =
                `<p>${error.message}</p>`;
        }
    };
}


async function loadRoadmap(resumeId) {
    const section = document.getElementById("roadmapSection");
    const resultElement = document.getElementById("roadmapResult");

    if (!section || !resultElement) return;

    section.style.display = "block";
    resultElement.style.display = "block";

    resultElement.innerHTML =
        "<p>Preparing your learning roadmap...</p>";

    try {
        const data = await apiRequest(
            `/career-advisor/roadmap?resume_id=${Number(resumeId)}`,
            {
                method: "POST"
            }
        );

        resultElement.innerHTML = `
            <div class="analysis-box">

                <h3>Your Learning Roadmap</h3>

                <p>
                    <strong>Missing Skills:</strong>
                    ${formatValue(data.missing_skills)}
                </p>

                <div>
                    ${formatValue(data.roadmap)}
                </div>

            </div>
        `;

    } catch (error) {
        console.error("Roadmap error:", error);

        resultElement.innerHTML =
            `<p>${error.message}</p>`;
    }
}


const generateRoadmapButton =
    document.getElementById("generateRoadmapButton");

if (generateRoadmapButton) {

    generateRoadmapButton.addEventListener("click", async () => {

        const resumeId =
            Number(generateRoadmapButton.dataset.resumeId);

        console.log("Generate Roadmap - Resume ID:", resumeId);

        if (!resumeId) {

            const resultElement =
                document.getElementById("roadmapResult");

            if (resultElement) {
                resultElement.style.display = "block";
                resultElement.innerHTML =
                    "<p>Please analyze a resume first.</p>";
            }

            return;
        }

        await loadRoadmap(resumeId);
    });
}

if (refreshResumes) {
    refreshResumes.addEventListener(
        "click",
        loadResumes
    );
}

if (logoutButton) {
    logoutButton.addEventListener("click", async () => {
        try {
            await apiRequest("/logout", {
                method: "POST"
            });
        } catch (error) {
            console.error(error);
        }

        window.location.href = "login.html";
    });
}

loadDashboardByRole();




/* =========================================================
   EMPLOYER DASHBOARD
========================================================= */

const jobForm = document.getElementById("jobForm");
const jobTitle = document.getElementById("jobTitle");
const jobContent = document.getElementById("jobContent");
const jobSkills = document.getElementById("jobSkills");
const jobMessage = document.getElementById("jobMessage");

const jobSearch = document.getElementById("jobSearch");
const jobList = document.getElementById("jobList");
const refreshJobs = document.getElementById("refreshJobs");


function formatSkills(skills) {

    if (!skills) {
        return "No skills specified";
    }

    if (Array.isArray(skills)) {
        return skills.join(", ");
    }

    return String(skills);
}


function renderJobs(jobs) {

    if (!jobList) return;

    if (!jobs || jobs.length === 0) {

        jobList.innerHTML =
            "<p>No jobs found.</p>";

        return;
    }

    jobList.innerHTML = jobs.map(job => `

        <div class="resume-item job-item">

            <div class="job-info">

                <h3>${job.title}</h3>

                <p>
                    ${job.content}
                </p>

                <p>
                    <strong>Required Skills:</strong>
                    ${formatSkills(job.required_skills)}
                </p>

                <p>
                    <strong>Job ID:</strong>
                    ${job.id}
                </p>

            </div>

            <div class="job-actions">

                <button
                    class="btn btn-secondary edit-job-button"
                    data-id="${job.id}"
                >
                    Edit
                </button>

                <button
                    class="btn btn-danger delete-job-button"
                    data-id="${job.id}"
                >
                    Delete
                </button>

            </div>

        </div>

    `).join("");


    document
        .querySelectorAll(".delete-job-button")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => deleteJob(button.dataset.id)
            );

        });


    document
        .querySelectorAll(".edit-job-button")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => editJob(button.dataset.id)
            );

        });
}


async function loadJobs(keyword = "") {

    if (!jobList) return;

    jobList.innerHTML =
        "<p>Loading jobs...</p>";

    try {

        let endpoint = "/jobs/";

        if (keyword.trim()) {

            endpoint =
                `/jobs/search?keyword=${encodeURIComponent(
                    keyword.trim()
                )}`;

        }

        const jobs =
            await apiRequest(endpoint);

        renderJobs(jobs);

    } catch (error) {

        console.error("Load jobs error:", error);

        jobList.innerHTML =
            `<p>${error.message}</p>`;
    }
}


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
                    .map(skill => skill.trim())
                    .filter(Boolean);


            if (!title || !content) {

                jobMessage.textContent =
                    "Please enter the job title and description.";

                return;
            }


            jobMessage.textContent =
                "Creating job...";


            try {

                await apiRequest(
                    "/jobs/",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            title,
                            content,
                            required_skills: skills
                        })
                    }
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


async function deleteJob(jobId) {

    if (!confirm("Are you sure you want to delete this job?")) {
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

        alert(error.message);
    }
}


async function editJob(jobId) {

    const title =
        prompt("New Job Title:");

    if (title === null) return;

    const content =
        prompt("New Job Description:");

    if (content === null) return;

    const skillsInput =
        prompt(
            "Required Skills (comma separated):"
        );

    if (skillsInput === null) return;


    const skills =
        skillsInput
            .split(",")
            .map(skill => skill.trim())
            .filter(Boolean);


    try {

        await apiRequest(
            `/jobs/${jobId}`,
            {
                method: "PUT",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    title: title.trim(),
                    content: content.trim(),
                    required_skills: skills
                })
            }
        );

        await loadJobs();

    } catch (error) {

        console.error(
            "Edit job error:",
            error
        );

        alert(error.message);
    }
}


if (refreshJobs) {

    refreshJobs.addEventListener(
        "click",
        () => loadJobs()
    );

}


if (jobSearch) {

    jobSearch.addEventListener(
        "input",
        () => loadJobs(jobSearch.value)
    );

}


async function loadDashboardByRole() {

    try {

        const user =
            await apiRequest("/me");

        console.log("Current user:", user);


        if (user.role === "employer") {

            if (jobSeekerDashboard) {
                jobSeekerDashboard.style.display = "none";
            }

            if (employerDashboard) {
                employerDashboard.style.display = "block";
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

        } else {

            if (jobSeekerDashboard) {
                jobSeekerDashboard.style.display = "block";
            }

            if (employerDashboard) {
                employerDashboard.style.display = "none";
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


loadDashboardByRole();




