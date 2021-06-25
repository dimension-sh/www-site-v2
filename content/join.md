---
title: "Join"
date: 2021-06-25T18:04:52+01:00
draft: false
---

Dimension is open to anyone who wants to be involved in our community, all we ask is that you follow the [RULES](/wiki/rules). If you accept them then joining is easy:

All you'll need to provide is the following bits of information:

{{< rawhtml >}}
    <form action="/cgi/join.cgi" method="post">
      <p><label for="username">Username</label><br />
        <input type="text" id="username" name="username">
      </p>
      <p><label for="email">Contact Email Address</label><br />
        <input type="text" id="email" name="email">
      </p>
      <p><label for="ssh_key">SSH Public Key</label><br />
        <textarea id="ssh_key" rows="5" cols="60" name="ssh_key"></textarea>
      </p>
      <p><label for="why">Why do you want to join?</label><br />
        <textarea id="why" rows="5" cols="60" name="why"></textarea>
      </p>
      <p><label for="rules">I have read the rules</label>
        <input type="checkbox" id="rules" name="rules" value="1">
      </p>
      <p><input type="submit" value="submit" /></p>
    </form>
{{< /rawhtml >}}