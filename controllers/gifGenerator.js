const spawn = require("child_process").spawn;
const uuid = require("uuid");
const Mail = require("./mail");
const config = require('../config');
const mailTemplate = "templates/email.html"

class GifGenerator {
    static run(queryParameters) {

        const fileName = uuid();
        const fileURL = `http://${config.serverURL}/${config.pathMainWeb}/generated/?${fileName}.gif`;
        const task = spawn("python", [
            "gifGenerator.py",
            "--bbox",
            queryParameters.bbox,
            "--output",
            fileName
        ]);

        console.log(`Running python ${task.pid} to output file ${fileName}`);
        task.stdout.on("data", (data) => console.log(data.toString()));
        task.stderr.on("data", (data) => console.log(`Error: ${data}`))
        task.on("close", (exitCode) => {

            if (exitCode != 0)
                return {"ok" : false, "msg" : "El correu no s'ha pogut enviar","codi" : 3, "error": `Python exitcode ${exitCode}`};
            
            const mail = new Mail(
                config.emailFrom,
                queryParameters.email,
                'Descàrrega fixer',
                mailTemplate
                );
            mail.swapTemplateVariable("{_FILE_PATH_}", fileURL);
            mail.send().then(() => {

                return {"ok" : true, "msg" : `Correu enviat a ${queryParameters.email}`};

            })
            .catch((error) => {

                return {"ok" : false, "msg" : "El correu no s'ha pogut enviar","codi" : 2, "error":error}

            });
            
        });

    }
}

module.exports = GifGenerator;
