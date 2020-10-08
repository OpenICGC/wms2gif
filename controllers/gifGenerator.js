const spawn = require("child_process").spawn;
const uuid = require("uuid");
const Mail = require("./mail");
const config = require('../config');
const mailTemplate = "templates/email.html"

class GifGenerator {
    static run(queryParameters) {

		const bbox = queryParameters.bbox.split(",");
		const centerX = (parseFloat(bbox[0]) + parseFloat(bbox[2]))/2.0;
		const centerY = (parseFloat(bbox[1]) + parseFloat(bbox[3]))/2.0;
        const fileName = `${uuid()}_${centerX.toFixed(8)}_${centerY.toFixed(8)}`;
		const fileURL = `https://${config.serverURL}/${config.pathMainWeb}/generated/?${fileName}.gif`;
		const start = Date.now();
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
				
			const time = Date.now() - start;
			console.log(`Process ran on ${time} milliseconds`);
            
            const mail = new Mail(
                config.emailFrom,
                queryParameters.email,
                'Descàrrega fitxer',
                mailTemplate
                );
            mail.swapTemplateVariable("{_FILE_PATH_}", fileURL);
            mail.send().then(() => {

                return {"ok" : true, "msg" : `Correu enviat a ${queryParameters.email} des de ${config.emailFrom}`};

            })
            .catch((error) => {

                return {"ok" : false, "msg" : "El correu no s'ha pogut enviar","codi" : 2, "error":error}

            });
            
        });

	}

}

module.exports = GifGenerator;
