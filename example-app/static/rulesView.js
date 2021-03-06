class RulesViewController {
    constructor(rules) {
        this.number_sequence = ko.observable(rules.number_sequence);
        this.number_sequence.subscribe(newValue => this.updateRule('number_sequence', newValue));

        this.uppercase = ko.observable(rules.uppercase);
        this.uppercase.subscribe(newValue => this.updateRule('uppercase', newValue));

        this.lowercase = ko.observable(rules.lowercase);
        this.lowercase.subscribe(newValue => this.updateRule('lowercase', newValue));

        this.punctuation = ko.observable(rules.punctuation);
        this.punctuation.subscribe(newValue => this.updateRule('punctuation', newValue));

        this.numbers = ko.observable(rules.numbers);
        this.numbers.subscribe(newValue => this.updateRule('numbers', newValue));

        this.username = ko.observable(rules.username);
        this.username.subscribe(newValue => this.updateRule('username', newValue));

        this.passwords = ko.observable(rules.passwords);
        this.passwords.subscribe(newValue => this.updateRule('passwords', newValue));

        this.keyboard_sequence = ko.observable(rules.keyboard_sequence);
        this.keyboard_sequence.subscribe(newValue => this.updateRule('keyboard_sequence', newValue));

        this.alphabet_sequence = ko.observable(rules.alphabet_sequence);
        this.alphabet_sequence.subscribe(newValue => this.updateRule('alphabet_sequence', newValue));

        this.pwned = ko.observable(rules.pwned);
        this.pwned.subscribe(newValue => this.updateRule('pwned', newValue));

        this.long_password_override = ko.observable(rules.long_password_override);
        this.long_password_override.subscribe(newValue => this.updateRule('long_password_override', newValue));

        this.min_password_length = ko.observable(rules.min_password_length);
        this.min_password_length.subscribe(newValue => this.updateRule('min_password_length', newValue));

        this.username_length = ko.observable(rules.username_length);
        this.username_length.subscribe(newValue => this.updateRule('username_length', newValue));

        this.show_hide_passwords = ko.observable(rules.show_hide_passwords);
        this.show_hide_passwords.subscribe(newValue => this.updateRule('show_hide_passwords', newValue));

        this.newRules = ko.observable('');
        ko.applyBindings(this);
    }

    static getInputValue(inputName) {
        const elements = document.getElementsByName(inputName);
        if (elements.length > 0)
            return elements[0].value;
        return ''
    }

    updateRule(name, value) {
        fetch(`/set_rule/${name}/${value}`
        ).then(response => response.text()
        ).then(response => this.newRules(response));
    }
}


document.addEventListener("DOMContentLoaded", (event) => {
    const value = RulesViewController.getInputValue('rules');
    const rules = JSON.parse(value);
    new RulesViewController(rules);

});

