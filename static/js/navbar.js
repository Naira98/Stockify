document
  .getElementById("profile-dropdown-trigger")
  .addEventListener("click", function () {
    const dropdown = document.getElementById("profile-dropdown");
    dropdown.classList.toggle("hidden");
  });

document.addEventListener("click", function (event) {
  const dropdown = document.getElementById("profile-dropdown");
  const trigger = document.getElementById("profile-dropdown-trigger");

  if (!trigger.contains(event.target) && !dropdown.contains(event.target)) {
    dropdown.classList.add("hidden");
  }
});
