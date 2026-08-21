const jobForm = document.getElementById("jobForm");
const jobTitle = document.getElementById("jobTitle");
const jobContent = document.getElementById("jobContent");
const jobSkills = document.getElementById("jobSkills");
const jobMessage = document.getElementById("jobMessage");

const jobSearch = document.getElementById("jobSearch");
const jobList = document.getElementById("jobList");
const refreshJobs = document.getElementById("refreshJobs");
const logoutButton = document.getElementById("logoutButton");


function formatSkills(skills) {
    if (!skills) return "No skills specified";

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
                    data-title="${encodeURIComponent(job.title)}"
                    data-content="${encodeURIComponent(job.content)}"
                    data-skills="${encodeURIComponent(
                        Array.isArray(job.required_skills)
                            ? job.required_skills.join(", ")
                            : ""
                    )}"
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
                () => editJob(button)
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
                    .filter(skill => skill.length > 0);


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
                            title: title,
                            content: content,
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

    const confirmed =
        confirm(
            "Are you sure you want to delete this job?"
        );

    if (!confirmed) return;


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


async function editJob(button) {

    const jobId =
        Number(button.dataset.id);

    const currentTitle =
        decodeURIComponent(
            button.dataset.title || ""
        );

    const currentContent =
        decodeURIComponent(
            button.dataset.content || ""
        );

    const currentSkills =
        decodeURIComponent(
            button.dataset.skills || ""
        );


    const newTitle =
        prompt(
            "Job Title:",
            currentTitle
        );

    if (newTitle === null) return;


    const newContent =
        prompt(
            "Job Description:",
            currentContent
        );

    if (newContent === null) return;


    const newSkills =
        prompt(
            "Required Skills (comma separated):",
            currentSkills
        );

    if (newSkills === null) return;


    const skills =
        newSkills
            .split(",")
            .map(skill => skill.trim())
            .filter(skill => skill.length > 0);


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
                    title: newTitle.trim(),
                    content: newContent.trim(),
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

                console.error(error);

            }

            window.location.href =
                "login.html";
        }
    );

}


window.loadEmployerJobs = loadJobs;

