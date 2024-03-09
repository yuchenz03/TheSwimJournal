//Function used to delete exercises from the coach exercise page
function deleteExercise(exerciseID) {
    if(confirm("Are you sure you want to delete this exercise?")) {
    fetch("/coach/delete-exercise", { //Sends a post request to delete-exercise endpoint
        method: "POST",
        body: JSON.stringify({ exerciseID: exerciseID })
    }).then((_res) => { //after recieving a response from endpoint, refresh page
        window.location.href = "/coach/Exercises";
    });
    };
}


//Function used to delete workout exercises from the coach workouts page
function deleteWorkoutExercise(workoutExerciseID) {
    if(confirm("Are you sure you want to delete this exercise?")) {
    fetch("/coach/delete-workout-exercise", { //Sends a post request to delete-exercise endpoint
        method: "POST",
        body: JSON.stringify({ workoutExerciseID: workoutExerciseID })
    }).then((_res) => { //after recieving a response from endpoint, refresh page
        window.location.href = "/coach/Workouts";
    });
    };
}