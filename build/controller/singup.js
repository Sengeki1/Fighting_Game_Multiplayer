const User = require("../schema/Schema");

const { createSecretToken } = require("../utils/generateToken");
const bcrypt = require("bcryptjs");

const createUser = async (req, res) => {
    try {
        if (!(req.body.email && req.body.password && req.body.name && req.body.username)) {
            res.status(400).send("Todos os campos são obrigatórios");
        }

        const oldUser = await User.findOne({ email: req.body.email });

        if (oldUser) {
            return res.status(409).send("User com esse e-mail já existe!");
        }
    
        const salt = 10;
        const hashedPassword = await bcrypt.hash(req.body.password, salt);
    
        const newUser = new User({
            name: req.body.name,
            username: req.body.username,
            email: req.body.email,
            password: hashedPassword,
        });
    
        const user = await newUser.save();
        const token = createSecretToken(user._id);
    
        res.cookie("token", token, {
            path: "/", // Cookie is accessible from all paths
            expires: new Date(Date.now() + 86400000), // Cookie expires in 1 day
            secure: true, // Cookie will only be sent over HTTPS
            httpOnly: true, // Cookie cannot be accessed via client-side scripts
            sameSite: "None",
        });
    
        console.log("cookie criado com sucesso!");
    
        res.json(user);
    } catch(err) {
        console.log("Erro: ", err)
    }
};
module.exports = createUser;

