const prevBtns = document.querySelectorAll(".btn-prev");
const nextBtns = document.querySelectorAll(".btn-next");
const progress = document.getElementById("progress");
const formSteps = document.querySelectorAll(".form-step");
const progressSteps = document.querySelectorAll(".progress-step");

let formStepsNum = 0;

nextBtns.forEach((btn) =>{
    btn.addEventListener('click', ()=>{
        formStepsNum++;
        updateFormSteps();
        updateProgressBar();
    });
});

prevBtns.forEach((btn) =>{
    btn.addEventListener('click', ()=>{
        formStepsNum--;
        updateFormSteps();
        updateProgressBar();
    });
});

function updateFormSteps(){
    formSteps.forEach((formStep) =>{
        formStep.classList.contains("form-step-active") && formStep.classList.remove("form-step-active");
    })

    formSteps[formStepsNum].classList.add('form-step-active')
}

function updateProgressBar(){
    progressSteps.forEach((progressStep, idx)=>{
        if(idx < formStepsNum + 1){
            progressStep.classList.add('progress-step-active');
        }else{
            progressStep.classList.remove('progress-step-active')
        }
    });
    const progressActive = document.querySelectorAll(".progress-step-active");
    progress.style.width = ((progressActive.length - 1) / (progressSteps.length - 1)) * 100 + "%";
}


// Loading button
function Loader() {
    window.addEventListener('submit', logSubmit);
    function logSubmit(event) {
      var loadingText = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
        if ( $(".btn").html() !== loadingText) {
            $(".btn").data('original-text', $(".btn").html());
            $(".btn").html(loadingText);

        }
        setTimeout(function () {
            $(".btn").html($(".btn").data('original-text'));
        }, 2000);
        event.preventDefault();
    }
}

let subform = document.getElementById('upload-form');
subform.addEventListener('submit', ()=>{
    let loading_animation = '<div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div>'
    let submit_btn = document.getElementById('submit-btn')
    submit_btn.html(loading_animation)
})