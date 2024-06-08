import './style.css'

let inputUsername = <HTMLInputElement> document.getElementById("username");
let inputPassword = <HTMLInputElement>  document.getElementById("password");
let btn = <HTMLButtonElement> document.querySelector("button");
let result = <HTMLElement> document.getElementById("result");

const HOST = "http://127.0.0.1:8000"


async function login() {
  let username = inputUsername.value;
  let password = inputPassword.value;
  let response: Response = await fetch( `${HOST}/auth/login`, {
    method: "post",
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
    body: JSON.stringify({
        "username": username,
        "password": password
      })
    },
  );
  switch(response.status){
    case 401:
      result.innerHTML = (await response.json()).detail;
      break;
    case 200:
      window.location.replace(`${HOST}/map`);
      break;
  }
  // if (response.status == 401){
  //   
  
  //    = res.;
  // }else{
  // }
}

btn.onclick = login;