exports.loginUser = (req, res, next) => {
    res.render('login/index',);
};

exports.singupUser = (req, res, next) => {
    res.render('register/index',);
};

exports.logout = (req, res, next) => {
    res.render('includes/successLogout',);
};