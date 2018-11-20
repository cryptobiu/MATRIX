const config = {
        apiKey: "insert_your_api_key",
        authDomain: "insert_your_auth_domain",
        databaseURL: "insert_your_database_url",
        projectId: "insert_your_project_id",
        storageBucket: "insert_your_storage_bucket",
        messagingSenderId: "insert_your_messaging_sender_id"
    };
firebase.initializeApp(config);



const txtEmail = document.getElementById('txtEmail');
const txtPassword = document.getElementById('txtPassword');
const btnLogin = document.getElementById('btnLogin');
const btnSignUp = document.getElementById('btnSignUp');
const btnLogout = document.getElementById('btnLogout');

// Add login event

btnLogin.addEventListener('click', e => {
  //get email and pass
  const email = txtEmail.value;
  const pass = txtPassword.value;
  const auth = firebase.auth();
  // Sign in
  const promise = auth.signInWithEmailAndPassword(email, pass);
  promise.catch(e => alert(e.code));

});

// Add signup event

btnSignUp.addEventListener('click', e=> {
  //get email and pass
  // TODO: check valid email address
  const email = txtEmail.value;
  const pass = txtPassword.value;
  const auth = firebase.auth();
  // Sign up
  const promise = auth.createUserWithEmailAndPassword(email, pass);
  promise.catch(e => alert(e.message));
});

btnLogout.addEventListener('click', e => {
    firebase.auth().signOut();
});


firebase.auth().onAuthStateChanged(firebaseUser => {
  if(firebaseUser) {
      btnLogout.classList.remove('hide');
      let user = firebase.auth().currentUser;
      console.log(user);
      if(user != null) {
          let uid = user.uid;
          let httpRequest = new XMLHttpRequest();
          httpRequest.open('POST', 'http://localhost:5000/', true);
          httpRequest.onreadystatechange = function (){
              if (httpRequest.readyState === 4 && httpRequest.status === 200 )
              {
                  console.log(uid);
              }
          };
          httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
          let dataRequest = {'user': uid};
          httpRequest.send(JSON.stringify(dataRequest));
          httpRequest.location.href = 'http://localhost:5000/home';
          btnLogin.classList.add('hide');
          //liork@gmail.com
      }
  } else {
      console.log('not logged in');
  }
});