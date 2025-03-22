// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBYvNrKLfgUppWl0G4yTCtM2hPiHi8r7pU",
  authDomain: "ecofin-fea31.firebaseapp.com",
  projectId: "ecofin-fea31",
  storageBucket: "ecofin-fea31.firebasestorage.app",
  messagingSenderId: "361643250514",
  appId: "1:361643250514:web:f92df3be9b4b7bf0e1e08b",
  measurementId: "G-8SQ5EZE48D"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);

export { app, auth }; 