"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const dotenv_1 = __importDefault(require("dotenv"));
const bodyParser = require("body-parser");
const supabase_js_1 = require("@supabase/supabase-js");
const cors = require("cors");
/*
 #####################################
 ############# CONFIG ################
 #####################################
*/
dotenv_1.default.config();
const db = (0, supabase_js_1.createClient)(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);
const app = (0, express_1.default)();
app.use(bodyParser.json());
app.use(cors());
// User
app.get("/users", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error, data } = yield db.from("Users").select("*");
    if (error)
        res.send(error), console.log(error);
    else
        res.send(data);
}));
app.post("/users/create", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    let user = req.body;
    console.log(user);
    const { error } = yield db.from("Users").insert({
        uuid: user.uuid,
        first_name: user === null || user === void 0 ? void 0 : user.first_name,
        last_name: user === null || user === void 0 ? void 0 : user.last_name,
        dob: user === null || user === void 0 ? void 0 : user.dob,
        start_date: user === null || user === void 0 ? void 0 : user.start_date,
        role: user === null || user === void 0 ? void 0 : user.role,
        department: user === null || user === void 0 ? void 0 : user.department,
        salary: user === null || user === void 0 ? void 0 : user.salary,
        phone_number: user === null || user === void 0 ? void 0 : user.phone_number
    });
    if (error) {
        console.log(error);
        res.send(error);
    }
    else {
        res.send(201);
    }
}));
app.post("/users/update", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    let user = req.body;
    const { error } = yield db.from("Users").update(user).eq('uuid', user.uuid);
    if (error) {
        console.log(error);
        res.send(error);
    }
    else {
        res.send(201);
    }
}));
app.post("/user/update-admins-number", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error } = yield db.from("Users").update({ phone_number: req.body.phone_number }).eq("role", "admin");
    if (error) {
        console.log(error);
        res.send(error);
    }
    else {
        res.send(201);
    }
}));
// Permissions
app.post("/permissions/grant", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error } = yield db.from("Permissions").insert({
        personnel_uuid: req.body.personnel_uuid,
        cabinet_id: req.body.cabinet_id
    });
    if (error) {
        console.log(error);
        res.send(error);
    }
    else {
        res.send(201);
    }
}));
app.post("/permissions/delete", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error } = yield db.from("Permissions").delete()
        .eq("personnel_uuid", req.body.personnel_uuid)
        .eq("cabinet_id", req.body.cabinet_id);
    if (error) {
        console.log(error);
        res.send(error);
    }
    else {
        res.send(201);
    }
}));
app.get("/permissions", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error, data } = yield db.from("Permissions").select("*");
    if (error)
        res.send(error), console.log(error);
    else
        res.send(data);
}));
// Status Events
app.post("/remote-unlock/", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    console.log(req);
    const { error } = yield db.from("Events").insert({
        event: "remote_unlock",
        cabinet_id: req.body.cabinet_id,
        user: "MASTER"
    });
    if (error) {
        console.log(error);
        res.send(error);
    }
    else {
        res.send(201);
    }
}));
app.get("/status-events", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error, data } = yield db.from("Events").select("*").order('id', { ascending: false });
    if (error)
        res.send(error), console.log(error);
    else
        res.send(data);
}));
// Item Types
app.get("/cabinets", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error, data } = yield db.from("Cabinets").select("*");
    if (error)
        res.send(error), console.log(error);
    else
        res.send(data);
}));
app.get("/item-types", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error, data } = yield db.from("ItemTypes").select("*");
    if (error)
        res.send(error), console.log(error);
    else
        res.send(data);
}));
app.post("/item-types/create", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error } = yield db.from("ItemTypes").insert({
        name: req.body.name
    });
    if (error) {
        console.log(error);
        res.send(error);
    }
    else {
        res.send(201);
    }
}));
app.post("/item-types/delete", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error } = yield db.from("ItemTypes").delete().eq("name", req.body.name);
    if (error) {
        console.log(error);
        res.send(error);
    }
    else {
        res.send(201);
    }
}));
// Items
app.get("/items", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { error, data } = yield db.from("Items").select("*");
    if (error)
        res.send(error), console.log(error);
    else
        res.send(data);
}));
app.post("/items/create", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    var _a, _b, _c, _d;
    const { error } = yield db.from("Items").insert({
        name: req.body.name,
        type: (_a = req.body) === null || _a === void 0 ? void 0 : _a.type,
        expiration: (_b = req.body) === null || _b === void 0 ? void 0 : _b.expiration,
        uuid: (_c = req.body) === null || _c === void 0 ? void 0 : _c.uuid,
        image: (_d = req.body) === null || _d === void 0 ? void 0 : _d.image
    });
    if (error) {
        console.log(error);
        res.send(error);
    }
    else {
        res.send(201);
    }
}));
app.post("/items/delete", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    var _e, _f;
    console.log(req);
    const { error } = yield db.from("Items").delete().eq("uuid", (_e = req.body) === null || _e === void 0 ? void 0 : _e.uuid).eq("name", (_f = req.body) === null || _f === void 0 ? void 0 : _f.name);
    if (error) {
        console.log(error);
        res.send(error);
    }
    else {
        res.send(201);
    }
}));
app.get("/", (req, res) => {
    res.send("Server running :)!");
});
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
