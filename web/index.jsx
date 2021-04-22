import React from "react";
import ReactDOM from "react-dom";
import Tool from "./Tool";

function bootstrap() {
  console.log("Meow: bootstrap");
  ReactDOM.render(<Tool />, document.getElementById("app"));
}

window.addEventListener('DOMContentLoaded', bootstrap);
