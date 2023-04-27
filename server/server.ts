import express, { Express, Request, Response } from 'express';
import dotenv from 'dotenv';
const bodyParser = require("body-parser");
import { createClient } from '@supabase/supabase-js'
const cors = require("cors");

/*
 #####################################
 ############# CONFIG ################
 #####################################
*/

dotenv.config();

const db = createClient(process.env.SUPABASE_URL as string, process.env.SUPABASE_KEY as string)

const app: Express = express();
app.use(bodyParser.json());
app.use(cors())


/*
 #####################################
 ############# ROUTES ################
 #####################################
*/

interface User {
    first_name: string,
    last_name: string,
    dob: string, // YYYY-MM-DD
    uuid: string,
    start_date: string, // YYYY-MM-DD
    role: string,
    department: string,
    salary: number,
    phone_number: string
}

// User
app.get("/users", async (req: Request, res: Response) => {
    const { error, data } = await db.from("Users").select("*")

    if (error) res.send(error), console.log(error);
    else   res.send(data)
})

app.post("/users/create", async (req: Request, res: Response) => {
    let user = req.body as User

    console.log(user)

    const { error } = await db.from("Users").insert({
        uuid: user.uuid,
        first_name: user?.first_name,
        last_name: user?.last_name,
        dob: user?.dob,
        start_date: user?.start_date,
        role: user?.role,
        department: user?.department,
        salary: user?.salary,
        phone_number: user?.phone_number
    })

    if (error) {
        console.log(error)
        res.send(error)
    }
    else {
        res.send(201)
    }
})

app.post("/users/update", async (req: Request, res: Response) => {
    let user = req.body as User

    const { error } = await db.from("Users").update(user).eq('uuid', user.uuid)

    if (error) {
        console.log(error)
        res.send(error)
    }
    else {
        res.send(201)
    }
})

app.post("/user/update-admins-number", async (req: Request, res: Response) => {
    const { error } = await db.from("Users").update({ phone_number: req.body.phone_number}).eq("role", "admin")

    if (error) {
        console.log(error)
        res.send(error)
    }
    else {
        res.send(201)
    }
})

// Permissions
app.post("/permissions/grant", async (req: Request, res: Response) => {

    const { error } = await db.from("Permissions").insert({
        personnel_uuid: req.body.personnel_uuid,
        cabinet_id: req.body.cabinet_id
    })

    if (error) {
        console.log(error)
        res.send(error)
    }
    else {
        res.send(201)
    }
})

app.post("/permissions/delete", async (req: Request, res: Response) => {
    const { error } = await db.from("Permissions").delete()
        .eq("personnel_uuid", req.body.personnel_uuid)
        .eq("cabinet_id", req.body.cabinet_id)

    
    if (error) {
        console.log(error)
        res.send(error)
    }
    else {
        res.send(201)
    }
})

app.get("/permissions", async (req: Request, res: Response) => {
    const { error, data } = await db.from("Permissions").select("*")

    if (error) res.send(error), console.log(error);
    else   res.send(data)
})

// Status Events
app.post("/remote-unlock/", async (req: Request, res: Response) => {
    console.log(req)

    const { error } = await db.from("Events").insert({
        event: "remote_unlock",
        cabinet_id: req.body.cabinet_id,
        user: "MASTER"
    })

    if (error) {
        console.log(error)
        res.send(error)
    }
    else {
        res.send(201)
    }
})

app.get("/status-events", async (req: Request, res: Response) => {
    const { error, data } = await db.from("Events").select("*").order('id', { ascending: false })

    if (error) res.send(error), console.log(error);
    else   res.send(data)
})

// Item Types
app.get("/cabinets", async (req: Request, res: Response) => {
    const { error, data } = await db.from("Cabinets").select("*")

    if (error) res.send(error), console.log(error);
    else   res.send(data)
})

app.get("/item-types", async (req: Request, res: Response) => {
    const { error, data } = await db.from("ItemTypes").select("*")

    if (error) res.send(error), console.log(error);
    else   res.send(data)
})

app.post("/item-types/create", async (req: Request, res: Response) => {
    const { error } = await db.from("ItemTypes").insert({
        name: req.body.name
    })

    if (error) {
        console.log(error)
        res.send(error)
    }
    else {
        res.send(201)
    }
})

app.post("/item-types/delete", async (req: Request, res: Response) => {
    const { error } = await db.from("ItemTypes").delete().eq("name", req.body.name)

    if (error) {
        console.log(error)
        res.send(error)
    }
    else {
        res.send(201)
    }
})

// Items
app.get("/items", async (req: Request, res: Response) => {
    const { error, data } = await db.from("Items").select("*")

    if (error) res.send(error), console.log(error);
    else   res.send(data)
})

app.post("/items/create", async (req: Request, res: Response) => {
    const { error } = await db.from("Items").insert({
        name: req.body.name,
        type: req.body?.type,
        expiration: req.body?.expiration,
        uuid: req.body?.uuid,
        image: req.body?.image
    })

    if (error) {
        console.log(error)
        res.send(error)
    }
    else {
        res.send(201)
    }
})

app.post("/items/delete", async (req: Request, res: Response) => {
    console.log(req)
    const { error } = await db.from("Items").delete().eq("uuid", req.body?.uuid).eq("name", req.body?.name)

    if (error) {
        console.log(error)
        res.send(error)
    }
    else {
        res.send(201)
    }
})

app.get("/", (req: Request, res: Response) => {
    res.send("Server running :)!")
})

const port = process.env.PORT || 8080;
app.listen(port, () => {
  console.log(`⚡️[server]: Server is running at http://localhost:${port}`);
});



// which are the not nullable fields?
/*
Cabinets
    - cabinet id

Events
    - event

ItemTypes
    - name

Items
    - name

Permissions
    - personnel_uuid
    - cabinet_id

Users
    - uuid

*/

/*



1. USER
POST
    - create user
        * profile pic
        * salary
        * ...

PUT
    - update user
        * ...

GET
    - select all

2. Cabinet
POST
    - Remote unlock (adds new status event)
    - update Authorized users (update where cabinet_id = &) =>
        - either add permissions OR 
        - take them away

GET
    - 

- see authorized users (get request)
- update authorized users

- remote unlock

- 

History of who's taken what


*/