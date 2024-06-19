const User = require("../schema/Schema");

const bcrypt = require("bcryptjs");
const env = require("dotenv");
const { createSecretToken } = require("../utils/generateToken");

env.config();

const login = async(req, res) => {
    const { password, username } = req.body;

    if (!(username && password)) {
        return res.json({ authentication: false });
    }

    const user = await User.findOne({ username });

    if (!(user && (await bcrypt.compare(password, user.password)))) {
        return res.json({ authentication: false });
    }

    const token = createSecretToken(user._id);

    res.cookie("token", token, {
        domain: process.env.MONGODB_URL, // Set your domain here
        path: "/", // Cookie is accessible from all paths
        expires: new Date(Date.now() + 86400000), // Cookie expires in 1 day
        secure: true, // Cookie will only be sent over HTTPS
        httpOnly: true, // Cookie cannot be accessed via client-side scripts
        sameSite: "None",
    });

    res.json({ token, authentication: true });
};
module.exports = login;