document.addEventListener("DOMContentLoaded", function () {
  const taskList = document.getElementById("task-list");

  function fetchTasks() {
    fetch("/tasks")
      .then((response) => response.json())
      .then((tasks) => {
        taskList.innerHTML = "";
        tasks.forEach((task) => {
          const taskElement = document.createElement("div");
          taskElement.classList.add("task");
          taskElement.innerHTML = `
                        <h3>${task.title}</h3>
                        <p>Description: ${task.description}</p>
                        <p>Status: ${task.status}</p>
                        <button class="update-btn" data-task-id="${task.id}">Update</button>
                        <button class="delete-btn" data-task-id="${task.id}">Delete</button>
                    `;
          taskList.appendChild(taskElement);
        });
      })
      .catch((error) => console.error("Error fetching tasks:", error));
  }

  fetchTasks(); // Fetch tasks when the page loads

  // Add event listener for form submission to add new task
  const taskForm = document.getElementById("task-form");
  taskForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const titleInput = document.getElementById("task-title");
    const titleValue = titleInput.value.trim(); // Trim whitespace

    // Validate title field
    if (titleValue === "") {
      alert("Please enter a title for the task.");
      return;
    }
    const descriptionInput = document.getElementById("task-description");
    const descriptionVal = descriptionInput.value.trim(); // Trim whitespace
    const statusInput = document.getElementById("task-status");
    const statValue = statusInput.value.trim(); // Trim whitespace

    const taskData = {
      title: titleValue,
      description: descriptionVal,
      status: statValue,
    };

    fetch("/tasks", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(taskData),
    })
      .then((response) => {
        if (response.ok) {
          return response.json(); // Return response JSON
        } else {
          console.error("Failed to add task:", response.statusText);
        }
      })
      .then((data) => {
        fetchTasks();
        taskForm.reset(); // Clear form inputs
      })
      .catch((error) => console.error("Error adding task:", error));
  });

  // Event listener for updating tasks
  taskList.addEventListener("click", function (event) {
    if (event.target.classList.contains("update-btn")) {
      const taskId = event.target.dataset.taskId;
      const fieldToUpdate = prompt(
        "Which field do you want to update? (title/description/status)"
      );
      const updatedValue = prompt(`Enter updated ${fieldToUpdate}:`);

      const updatedData = {};
      updatedData[fieldToUpdate] = updatedValue;

      fetch(`/tasks/${taskId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedData),
      })
        .then((response) => {
          if (response.ok) {
            return response.json();
          } else {
            console.error("Failed to update task:", response.statusText);
          }
        })
        .then((data) => {
          fetchTasks();
        })
        .catch((error) => console.error("Error updating task:", error));
    }
  });

  // Event listener for deleting tasks
  taskList.addEventListener("click", function (event) {
    if (event.target.classList.contains("delete-btn")) {
      const taskId = event.target.dataset.taskId;
      if (confirm("Are you sure you want to delete this task?")) {
        fetch(`/tasks/${taskId}`, {
          method: "DELETE",
        })
          .then((response) => {
            if (response.ok) {
              return response.json();
            } else {
              console.error("Failed to delete task:", response.statusText);
            }
          })
          .then((data) => {
            fetchTasks();
          })
          .catch((error) => console.error("Error deleting task:", error));
      }
    }
  });
});

