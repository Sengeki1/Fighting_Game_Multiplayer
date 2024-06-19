const express = require('express');
const adminController = require('../controller/admin');
const loginController  = require('../controller/login')
const singUpController  = require('../controller/singup')

const router = express.Router();

router.get('/loginUser', adminController.loginUser); // login routes

router.post('/login', loginController);


router.get('/singupUser', adminController.singupUser); // register routes

router.post('/singup', singUpController);


router.get('/logout', adminController.logout); // logout route

module.exports = router