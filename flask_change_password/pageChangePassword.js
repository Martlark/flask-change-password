class FlaskChangePasswordViewModel {
    constructor() {
        this.tickCharacter = "&#10003;";
        this.message = ko.observable("");
        this.changing = ko.observable(this.getInputValue("changing") == "True");
        this.old_password = ko.observable(this.getInputValue("old_password"));
        this.password1 = ko.observable(this.getInputValue("password"));
        this.password1Strength = ko.observable(-1);
        this.password2 = ko.observable(this.getInputValue("password2"));
        this.old_passwordMessageOK = ko.observable("");
        this.password1MessageOK = ko.observable("");
        this.password1Message = ko.observable(" ");
        this.password2Message = ko.observable(" ");
        this.password2MessageOK = ko.observable("");
        this.old_passwordMessage = ko.observable("");
        this.minPasswordCheckLength = Number(this.getInputValue("password_length"));
        this.showHidePassword = ko.observable(true);
        this.rules = {};

        fetch('/flask_change_password/get_rules').then(result => result.json()).then(result => {
            this.rules = result;
            if (Number(this.minPasswordCheckLength) <= 0) {
                this.minPasswordCheckLength = Number(this.rules.min_password_length)
            }
            this.showHidePassword(this.rules.show_hide_passwords)
        });
        this.addMessageSpans();
        this.previous = {};
        this.old_passwordMessage.subscribe(newValue => this.old_passwordCheck());
        this.password1Message.subscribe(newValue => this.password1Check());
        this.password2Message.subscribe(newValue => this.password2Check());
        // start knockout up.
        ko.applyBindings(this, document.getElementById('change_password_div'));
        setInterval(() => {
            this.intervalHandler();
        }, 1500);
        this.messages = {
            currentPasswordRequired: 'Current password required',
            passwordNotLongEnough: "password not long enough",
            passwordNotDifferentFomCurrentPassword: "password not different from current password",
            moreCharactersRequired: "more characters required",
            passwordsDoNotMatch: "passwords do not match",
            insufficient: "",
        };
    }

    getInputValue(inputName) {
        const elements = document.getElementsByName(inputName);
        if (elements.length > 0)
            return elements[0].value;
        return ''
    }

    intervalHandler() {
        const previousCheck = {a: this.old_password(), b: this.password1(), c: this.password2()};
        if (JSON.stringify(previousCheck) === JSON.stringify(this.previous)) {
            return;
        }
        this.previous = previousCheck;
        if (this.changing() && this.old_password().length < this.minPasswordCheckLength) {
            this.old_passwordMessage(this.messages.currentPasswordRequired);
        } else {
            this.old_passwordMessage("");
        }

        if (this.password1().length < this.minPasswordCheckLength) {
            this.password1Message(this.messages.passwordNotLongEnough);
        } else if (this.changing() && this.password1() == this.old_password()) {
            this.password1Message(this.messages.passwordNotDifferentFomCurrentPassword);
        } else {
            this.checkPassword1(this.password1());
        }

        if (this.password1().length >= this.minPasswordCheckLength) {
            if (this.password1() != this.password2()) {
                if (this.password2().length < this.minPasswordCheckLength) {
                    this.password2Message(this.messages.moreCharactersRequired);
                } else {
                    this.password2Message(this.messages.passwordsDoNotMatch);
                }
                return;
            } else {
                this.password2Message("");
            }
        }

    }

    password1Check() {
        if (this.password1Message().length == 0)
            this.password1MessageOK(this.tickCharacter);
        else
            this.password1MessageOK("");

    }

    old_passwordCheck() {
        if (this.old_passwordMessage().length == 0)
            this.old_passwordMessageOK(this.tickCharacter);
        else
            this.old_passwordMessageOK("");
    }

    password2Check() {
        if (this.password2Message().length == 0)
            this.password2MessageOK(this.tickCharacter);
        else
            this.password2MessageOK("");
    }

    verified() {
        if (this.password1().length == 0 || this.password2().length == 0) {
            return false;
        }
        if (this.changing() && this.old_password().length == 0) {
            return false;
        }
        return this.password1Message().length <= 1 && this.password2Message().length <= 1;
    }

    addMessageSpans() {
        if (this.changing()) {
            this.insertAfterByName(["<span class='alert-danger' data-bind='text:old_passwordMessage'></span>", "<span>&nbsp;</span>"], "old_password");
            this.insertAfterByName(["<span class='alert-success' data-bind='html:old_passwordMessageOK'></span>", "<span>&nbsp;</span>"], "old_password");
        }
        this.insertAfterByName(["<span class='alert-danger' data-bind='text:password1Message'></span>"], "password");
        this.insertAfterByName(["<span class='alert-success' data-bind='html:password1MessageOK'></span>", "<span>&nbsp;</span>"], "password");
        this.insertAfterByName(["<span class='alert-danger' data-bind='text:password2Message'></span>"], "password2");
        this.insertAfterByName(["<span class='alert-success' data-bind='html:password2MessageOK'></span>", "<span>&nbsp;</span>"], "password2");
    }

    createElementFromHTML(htmlString) {
        const div = document.createElement('div');
        div.innerHTML = htmlString.trim();

        // Change this to div.childNodes to support multiple top-level nodes
        return div.firstChild;
    }

    insertAfterByName(nodeTextList, name) {
        const referenceNode = document.getElementsByName(name)[0];
        if (referenceNode) {
            nodeTextList.forEach(nodeText => {
                const node = this.createElementFromHTML(nodeText);
                referenceNode.parentNode.insertBefore(node, node.nextSibling)
            });
        } else {
            console.log("name not found", name);
        }
    }

    serialize(id) {
        // serialize form
        const form = document.getElementById("change_password_form");
        const data = {};
        const inputs = [].slice.call(form.getElementsByTagName('input'));
        inputs.forEach(input => {
            data[input.name] = input.value;
        });
        return JSON.stringify(data);
    }

    checkPassword1(password, messageMethod) {
        try {
            const data = this.serialize("change_password_form");
            const csrf_token = this.getInputValue('csrf_token');
            fetch(
                "/flask_change_password/check_password",
                {
                    method: "POST",
                    headers: {
                        'Accept': 'text/html',
                        'Content-Type': 'application/json',
                        "X-CSRFToken": csrf_token,
                    },
                    body: data,
                }).then(result => result.text()).then(result => {
                if (isNaN(result)) {
                    this.password1Message(result);
                    this.password1Strength(0);
                } else {
                    this.password1Strength(Number(result));
                    this.password1Message("");
                    return true;
                }
            });
        } catch (e) {
            this.message(`${e.statusText || ""} - problem found - refresh page`);
        }
        return false;
    }

    clickToggleShowPassword(view, evt) {
        if (this.showHidePassword()) {
            const label = evt.currentTarget;
            const input = document.getElementById(label.htmlFor);
            if (input.type === "password") {
                input.type = "text";
            } else {
                input.type = "password";
            }
        }
    }
}

//let KO know that we will take care of managing the bindings of our children

ko.bindingHandlers.stopBinding = {
    init: function () {
        return {controlsDescendantBindings: true};
    }
};

//KO 2.1, now allows you to add containerless support for custom bindings
ko.virtualElements.allowedBindings.stopBinding = true;


document.addEventListener("DOMContentLoaded", (event) => {
    new FlaskChangePasswordViewModel();

});

